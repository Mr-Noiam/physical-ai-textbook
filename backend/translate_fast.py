"""
Fast translation script - translates entire files at once using Gemini API.
Much faster than line-by-line translation.
"""

import sys
import time
from pathlib import Path
import requests

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# API Configuration
API_BASE_URL = "http://localhost:8000"
TRANSLATE_URL = f"{API_BASE_URL}/api/v1/translate"

# Paths
DOCS_DIR = Path("../docusaurus/docs")
URDU_DOCS_DIR = Path("../docusaurus/i18n/ur/docusaurus-plugin-content-docs/current")

def translate_text(text: str) -> str:
    """Translate text using backend API."""
    try:
        response = requests.post(TRANSLATE_URL, json={
            "content": text,
            "target_language": "ur",
            "source_language": "en",
            "use_cache": True
        }, timeout=180)

        if response.status_code == 200:
            return response.json()['translated_content']
        else:
            print(f"    ERROR: API returned {response.status_code}")
            return text

    except Exception as e:
        print(f"    ERROR: {str(e)[:100]}")
        return text

def translate_file(input_file: Path, output_file: Path):
    """Translate entire markdown file at once."""
    print(f"\n  Translating: {input_file.name}")

    # Read file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Translate entire content
    print(f"    Sending to Gemini API ({len(content)} chars)...")
    translated_content = translate_text(content)

    # Save
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(translated_content)

    print(f"    ✓ Saved: {output_file.name}")

def main():
    """Main entry point."""
    print("=" * 60)
    print("FAST TRANSLATION TO URDU")
    print("=" * 60)

    # Ensure directory exists
    URDU_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Find all markdown files
    md_files = list(DOCS_DIR.rglob("*.md"))
    print(f"\nTranslating {len(md_files)} files...\n")

    # Translate each file
    for i, md_file in enumerate(md_files, 1):
        rel_path = md_file.relative_to(DOCS_DIR)
        output_file = URDU_DOCS_DIR / rel_path

        print(f"[{i}/{len(md_files)}]", end=" ")
        translate_file(md_file, output_file)

        # Small delay to respect rate limits
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("✓ TRANSLATION COMPLETE!")
    print("=" * 60)
    print(f"\nUrdu files: {URDU_DOCS_DIR}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
