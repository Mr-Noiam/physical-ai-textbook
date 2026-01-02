# backend/scripts/translate_content.py

import os
import json
import re
from pathlib import Path
import time
import hashlib

# --- Configuration ---

# The root directory of the docusaurus project
DOCUSAURUS_ROOT = Path(__file__).parent.parent.parent / "docusaurus"

# The directory containing the original English markdown files
SOURCE_DIR = DOCUSAURUS_ROOT / "docs"

# The base directory for i18n translations
I18N_DIR = DOCUSAURUS_ROOT / "i18n"

# The target directory for the translated Urdu files
TARGET_DIR = I18N_DIR / "ur" / "docusaurus-plugin-content-docs" / "current"

# The path to the translation cache file
CACHE_FILE = Path(__file__).parent / "translation_cache.json"

# --- Mock Translation Function ---

def get_translation(line: str, cache: dict) -> str:
    """
    Translates a line of text to Urdu, using a cache.
    Skips lines that appear to be syntax and not content.
    """
    stripped_line = line.strip()

    # Heuristic: Do not translate lines that are empty or look like code/syntax
    if (
        not stripped_line
        or stripped_line.startswith('```')
        or stripped_line.startswith('---')
        or stripped_line.startswith('!')
        or '<' in stripped_line # Safest check: if it has a tag, don't touch it
    ):
        return line

    # This is a line we can translate
    cache_key = hashlib.sha256(stripped_line.encode('utf-8')).hexdigest()
    if cache_key in cache:
        # Return from cache, preserving original indentation + newline
        return line.replace(stripped_line, cache[cache_key])
    
    # --- Replace this block with your translation API call ---
    time.sleep(0.01) 
    translated_text = f"[URDU] {stripped_line}"
    # --- End of replacement block ---

    # Store the new translation in the cache
    cache[cache_key] = translated_text
    print(f"Translated and cached new line (key: {cache_key[:6]}...).\n")
    
    return line.replace(stripped_line, translated_text)

# --- Main Script Logic ---

def main():
    """
    Main function to translate markdown files from English to Urdu.
    """
    print("Starting translation process...")
    
    # Load translation cache
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            translation_cache = json.load(f)
        print(f"Loaded {len(translation_cache)} translations from cache.")
    else:
        translation_cache = {}
        print("No cache file found. Starting with an empty cache.")

    # Find all markdown files in the source directory
    source_files = list(SOURCE_DIR.rglob("*.md")) + list(SOURCE_DIR.rglob("*.mdx"))
    
    if not source_files:
        print(f"Error: No markdown files found in {SOURCE_DIR}. Nothing to translate.")
        return

    print(f"Found {len(source_files)} markdown files to process.")

    for source_file in source_files:
        relative_path = source_file.relative_to(SOURCE_DIR)
        target_file = TARGET_DIR / relative_path
        
        print(f"\nProcessing: {source_file.name}")
        
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        translated_lines = []
        in_code_block = False
        in_frontmatter = False

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
                in_code_block = not in_code_block
            
            if in_code_block:
                translated_lines.append(line)
                continue
            
            # If not in frontmatter or code, attempt translation
            translated_line = get_translation(line, translation_cache)
            translated_lines.append(translated_line)

        translated_content = "".join(translated_lines)
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(translated_content)
            
        print(f"  -> Saved translated file to: {target_file}")

    # Save the updated cache
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(translation_cache, f, ensure_ascii=False, indent=2)
        
    print(f"\nTranslation process complete. Cache saved with {len(translation_cache)} entries.")


if __name__ == "__main__":
    main()
