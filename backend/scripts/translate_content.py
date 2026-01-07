# backend/scripts/translate_content.py

import os
import sys
import json
import re
from pathlib import Path
import time
import hashlib
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import argparse

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Explicitly load environment variables from the .env file located in the backend directory
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

from app.services.translation import translate_multiple, TranslationResponse
from app.db.neon import get_db

# --- Configuration ---

# The root directory of the docusaurus project
DOCUSAURUS_ROOT = Path(__file__).parent.parent.parent / "docusaurus"

# The directory containing the original English markdown files
SOURCE_DIR = DOCUSAURUS_ROOT / "docs"

# The base directory for i18n translations
I18N_DIR = DOCUSAURUS_ROOT / "i18n"

# The target directory for the translated Urdu files
TARGET_DIR = I18N_DIR / "ur" / "docusaurus-plugin-content-docs" / "current"

# Target module to translate (set via environment variable, default to Module 1)
TARGET_MODULE = os.getenv("TRANSLATE_MODULE", "module-1-ros2")

# Whether to skip existing translated files
SKIP_EXISTING = os.getenv("SKIP_EXISTING", "false").lower() == "true"

def should_translate(line: str) -> bool:
    """
    Determines if a line should be translated.
    """
    stripped_line = line.strip()
    return not (
        not stripped_line
        or len(stripped_line) < 3
        or stripped_line.startswith('```')
        or stripped_line.startswith('---')
        or stripped_line.startswith('!')
        or '<' in stripped_line
    )

def process_translation(
    lines: list[str], db: Session, chapter_path: str, max_retries: int = 3
) -> list[str]:
    """
    Processes a list of lines for translation.
    """
    if not lines:
        return []

    # Attempt to translate the entire block
    for attempt in range(max_retries):
        try:
            results = translate_multiple(
                contents=lines,
                target_language="ur",
                source_language="en",
                db=db,
            )
            # This is a bit of a hack, translate_multiple should probably take the chapter_path
            # For now, we assume all lines are from the same chapter
            for i, result in enumerate(results):
                if not result.cached:
                    from app.services.translation import save_translation_to_cache
                    save_translation_to_cache(
                        db,
                        original_content=lines[i],
                        translated_content=result.translated_content,
                        target_language="ur",
                        chapter_path=chapter_path,
                    )
            return [result.translated_content for result in results]
        except Exception as e:
            error_msg = str(e)
            print(f"  ⚠ Attempt {attempt + 1}/{max_retries} failed: {error_msg[:80]}...")
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"    Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
            if attempt == max_retries - 1:
                print(f"  ✗ Translation failed after {max_retries} attempts. Keeping original text.")
                return lines
    return lines


import argparse

# --- Main Script Logic ---

def main():
    """
    Main function to translate markdown files from English to Urdu.
    """
    parser = argparse.ArgumentParser(description="Translate markdown files from English to Urdu.")
    parser.add_argument("--file", type=str, help="Translate a single file.")
    args = parser.parse_args()

    print("=" * 70)
    print("URDU TRANSLATION SCRIPT")
    print("=" * 70)
    
    if args.file:
        print(f"Target file: {args.file}")
    else:
        print(f"Target module: {TARGET_MODULE}")
        
    print(f"Skip existing: {SKIP_EXISTING}")
    print("=" * 70)

    # Initialize DB session for translation service
    db_session = next(get_db())
    print("✓ Database session initialized for translation service.")
    print()

    try:
        if args.file:
            source_files = [SOURCE_DIR / args.file]
        else:
            # Find markdown files based on TARGET_MODULE
            if TARGET_MODULE == "all":
                source_files = list(SOURCE_DIR.rglob("*.md")) + list(SOURCE_DIR.rglob("*.mdx"))
            else:
                # Only process specific module
                module_dir = SOURCE_DIR / TARGET_MODULE
                if module_dir.exists():
                    source_files = list(module_dir.glob("*.md")) + list(module_dir.glob("*.mdx"))
                else:
                    print(f"✗ Error: Module directory {module_dir} not found.")
                    return

        if not source_files:
            print(f"✗ Error: No markdown files found in {SOURCE_DIR / TARGET_MODULE}.")
            return

        print(f"Found {len(source_files)} markdown files to translate.")

        for idx, source_file in enumerate(source_files, 1):
            relative_path = source_file.relative_to(SOURCE_DIR)
            target_file = TARGET_DIR / relative_path

            print(f"\n[{idx}/{len(source_files)}] Processing: {source_file.name}")
            print(f"  Source: {relative_path}")

            if SKIP_EXISTING and target_file.exists():
                print("  ✓ Skipping existing file.")
                continue

            target_file.parent.mkdir(parents=True, exist_ok=True)

            with open(source_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            translated_lines = []
            in_code_block = False
            in_frontmatter = False
            chunk_to_translate = []

            if lines and lines[0].strip() == '---':
                in_frontmatter = True

            for i, line in enumerate(lines):
                # Handle Frontmatter
                if in_frontmatter:
                    translated_lines.append(line)
                    if line.strip() == '---' and i > 0:
                        in_frontmatter = False
                    continue

                # Handle Code Blocks
                if line.strip().startswith('```'):
                    if chunk_to_translate:
                        results = translate_multiple(
                            contents=chunk_to_translate,
                            db=db_session,
                            chapter_path=relative_path.as_posix(),
                        )
                        translated_lines.extend(
                            [result.translated_content for result in results]
                        )
                        chunk_to_translate = []
                    in_code_block = not in_code_block
                    translated_lines.append(line)
                    continue

                if in_code_block:
                    translated_lines.append(line)
                    continue
                
                # If not in frontmatter or code, check if we should translate
                if should_translate(line):
                    chunk_to_translate.append(line)
                else:
                    if chunk_to_translate:
                        results = translate_multiple(
                            contents=chunk_to_translate,
                            db=db_session,
                            chapter_path=relative_path.as_posix(),
                        )
                        translated_lines.extend(
                            [result.translated_content for result in results]
                        )
                        chunk_to_translate = []
                    translated_lines.append(line)

            if chunk_to_translate:
                results = translate_multiple(
                    contents=chunk_to_translate,
                    db=db_session,
                    chapter_path=relative_path.as_posix(),
                )
                translated_lines.extend(
                    [result.translated_content for result in results]
                )

            translated_content = "".join(translated_lines)

            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)

            print(f"  ✓ Saved: {target_file}")

        print("\n" + "=" * 70)
        print("✓ TRANSLATION COMPLETE!")
        print("=" * 70)
        print(f"Processed {len(source_files)} files")
        print(f"Target module: {TARGET_MODULE}")
        print("=" * 70)

    finally:
        db_session.close()
        print("✓ Database session closed.")


if __name__ == "__main__":
    main()
