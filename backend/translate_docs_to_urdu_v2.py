"""
Pre-translate all documentation to Urdu - Optimized Version

This version translates content in larger chunks for better performance.
"""

import sys
import time
from pathlib import Path
import requests

# Fix Windows console encoding for Unicode/Urdu characters
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

def ensure_urdu_dir():
    """Create Urdu docs directory if it doesn't exist."""
    URDU_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Created Urdu docs directory: {URDU_DOCS_DIR}")

def translate_text(text: str, target_language: str = "ur") -> str:
    """Translate text using backend API."""
    try:
        response = requests.post(TRANSLATE_URL, json={
            "content": text,
            "target_language": target_language,
            "source_language": "en",
            "use_cache": True
        }, timeout=120)  # Increased timeout for larger chunks

        if response.status_code == 200:
            data = response.json()
            return data['translated_content']
        else:
            print(f"    ERROR: Translation API returned {response.status_code}")
            return text  # Return original if translation fails

    except requests.exceptions.Timeout:
        print(f"    ERROR: Translation timed out (text too long)")
        return text
    except requests.exceptions.RequestException as e:
        print(f"    ERROR: {str(e)[:100]}")
        return text

def translate_markdown_file_optimized(input_file: Path, output_file: Path):
    """
    Translate a markdown file from English to Urdu.

    Uses paragraph-based batching for better performance.
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

    # Process content
    lines = main_content.split('\n')
    translated_lines = []

    in_code_block = False
    text_buffer = []  # Buffer to collect text lines
    chunk_count = 0

    def flush_buffer():
        """Translate accumulated text buffer"""
        nonlocal chunk_count
        if not text_buffer:
            return

        # Join lines with newlines
        chunk = '\n'.join(text_buffer)

        # Translate the whole chunk
        print(f"    Translating chunk {chunk_count + 1} ({len(chunk)} chars)...")
        translated_chunk = translate_text(chunk)

        # Split back into lines
        translated_chunk_lines = translated_chunk.split('\n')
        translated_lines.extend(translated_chunk_lines)

        text_buffer.clear()
        chunk_count += 1

        # Small delay between chunks
        time.sleep(0.3)

    for line in lines:
        # Check for code block markers
        if line.strip().startswith('```'):
            # Flush any pending text before code block
            flush_buffer()
            in_code_block = not in_code_block
            translated_lines.append(line)
            continue

        # Skip translation inside code blocks
        if in_code_block:
            flush_buffer()  # Flush before code
            translated_lines.append(line)
            continue

        # Skip empty lines (but preserve them)
        if not line.strip():
            flush_buffer()  # Flush before empty line
            translated_lines.append(line)
            continue

        # Skip lines that are just markdown syntax
        if all(c in '-*_= ' for c in line.strip()):
            flush_buffer()
            translated_lines.append(line)
            continue

        # Accumulate text lines into buffer
        text_buffer.append(line)

        # Flush buffer after ~15 lines or ~3000 chars to avoid API limits
        # (422 errors occur with chunks larger than ~10000 chars)
        buffer_size = sum(len(l) for l in text_buffer)
        if len(text_buffer) >= 15 or buffer_size > 3000:
            flush_buffer()

    # Flush any remaining text
    flush_buffer()

    # Combine everything
    urdu_content = frontmatter + '\n' + '\n'.join(translated_lines)

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write translated file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(urdu_content)

    print(f"    Saved: {output_file}")
    print(f"    Stats: {chunk_count} chunks translated")

def translate_all_docs():
    """Translate all documentation files to Urdu."""
    print("=" * 70)
    print("TRANSLATING DOCUMENTATION TO URDU (OPTIMIZED)")
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
        translate_markdown_file_optimized(md_file, output_file)

    print("\n" + "=" * 70)
    print("TRANSLATION COMPLETE!")
    print("=" * 70)
    print(f"\nTranslated files saved to: {URDU_DOCS_DIR}")

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
