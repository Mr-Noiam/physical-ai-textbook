"""
Pre-translate all documentation to Urdu and save as markdown files.

This creates Urdu versions of all docs that can be served statically,
instead of translating on-demand (which is slow and can fail).
"""

import os
import sys
import time
from pathlib import Path
import requests

# API Configuration
API_BASE_URL = "http://localhost:8000"
TRANSLATE_URL = f"{API_BASE_URL}/api/v1/translate"

# Paths
DOCS_DIR = Path("../docusaurus/docs")
URDU_DOCS_DIR = Path("../docusaurus/i18n/ur/docusaurus-plugin-content-docs/current")

def ensure_urdu_dir():
    """Create Urdu docs directory if it doesn't exist."""
    URDU_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created Urdu docs directory: {URDU_DOCS_DIR}")

def translate_text(text: str, target_language: str = "ur") -> str:
    """Translate text using backend API."""
    try:
        response = requests.post(TRANSLATE_URL, json={
            "content": text,
            "target_language": target_language,
            "source_language": "en",
            "use_cache": True
        }, timeout=30)

        if response.status_code == 200:
            data = response.json()
            return data['translated_content']
        else:
            print(f"    ERROR: Translation API returned {response.status_code}")
            print(f"    {response.text[:200]}")
            return text  # Return original if translation fails

    except requests.exceptions.RequestException as e:
        print(f"    ERROR: {str(e)[:100]}")
        return text  # Return original if request fails

def translate_markdown_file(input_file: Path, output_file: Path):
    """
    Translate a markdown file from English to Urdu.

    Preserves:
    - Frontmatter (YAML at top)
    - Code blocks
    - Links
    - Special markdown syntax

    Translates:
    - Headings
    - Paragraphs
    - List items
    """
    print(f"\nTranslating: {input_file.name}")

    # Read original file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split frontmatter and content
    parts = content.split('---', 2)
    if len(parts) >= 3 and content.startswith('---'):
        frontmatter = f"---{parts[1]}---"
        main_content = parts[2]
    else:
        frontmatter = ""
        main_content = content

    # Split content into lines
    lines = main_content.split('\n')
    translated_lines = []

    in_code_block = False
    translated_count = 0
    skipped_count = 0

    for line in lines:
        # Check for code block markers
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            translated_lines.append(line)  # Keep code block markers as-is
            continue

        # Skip translation inside code blocks
        if in_code_block:
            translated_lines.append(line)
            skipped_count += 1
            continue

        # Skip empty lines
        if not line.strip():
            translated_lines.append(line)
            continue

        # Skip lines that are just markdown syntax (like ---, ***, etc.)
        if all(c in '-*_=' for c in line.strip()):
            translated_lines.append(line)
            continue

        # Translate content lines
        try:
            # Extract the text to translate (preserve markdown formatting)
            stripped = line.strip()

            # Skip very short lines or lines with just punctuation
            if len(stripped) < 3 or all(c in '.,!?;:-()[]{}' for c in stripped):
                translated_lines.append(line)
                continue

            # Translate
            translated_text = translate_text(stripped)

            # Preserve original indentation
            indent = len(line) - len(line.lstrip())
            translated_line = ' ' * indent + translated_text

            translated_lines.append(translated_line)
            translated_count += 1

            # Show progress
            if translated_count % 5 == 0:
                print(f"    Translated {translated_count} lines...")

            # Rate limiting (avoid overwhelming API)
            time.sleep(0.2)

        except Exception as e:
            print(f"    ERROR translating line: {str(e)[:50]}")
            translated_lines.append(line)  # Keep original on error

    # Combine everything
    urdu_content = frontmatter + '\n' + '\n'.join(translated_lines)

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write translated file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(urdu_content)

    print(f"    ✓ Saved: {output_file}")
    print(f"    Stats: {translated_count} translated, {skipped_count} skipped (code blocks)")

def translate_all_docs():
    """Translate all documentation files to Urdu."""
    print("=" * 70)
    print("TRANSLATING DOCUMENTATION TO URDU")
    print("=" * 70)

    # Ensure Urdu directory exists
    ensure_urdu_dir()

    # Find all markdown files
    md_files = list(DOCS_DIR.rglob("*.md"))

    print(f"\nFound {len(md_files)} markdown files to translate\n")

    # Translate each file
    for i, md_file in enumerate(md_files, 1):
        # Get relative path
        rel_path = md_file.relative_to(DOCS_DIR)

        # Output path (same structure in Urdu dir)
        output_file = URDU_DOCS_DIR / rel_path

        print(f"\n[{i}/{len(md_files)}]", end=" ")
        translate_markdown_file(md_file, output_file)

    print("\n" + "=" * 70)
    print("TRANSLATION COMPLETE!")
    print("=" * 70)
    print(f"\nTranslated files saved to: {URDU_DOCS_DIR}")
    print("\nNext steps:")
    print("1. Review translated files")
    print("2. Configure Docusaurus i18n for Urdu")
    print("3. Build and test")

def main():
    """Main entry point."""
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("ERROR: Backend not responding properly")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("ERROR: Backend not running!")
        print("\nPlease start the backend first:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload")
        sys.exit(1)

    # Run translation
    try:
        translate_all_docs()
    except KeyboardInterrupt:
        print("\n\nTranslation interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
