"""
Translate week4-urdf.md to complete Module 1 translation
"""

import sys
from pathlib import Path
import requests
import time

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

# File paths
SOURCE_FILE = Path("../docusaurus/docs/module-1-ros2/week4-urdf.md")
OUTPUT_FILE = Path("../docusaurus/i18n/ur/docusaurus-plugin-content-docs/current/module-1-ros2/week4-urdf.md")

def split_markdown(text: str, max_chars: int = 9000) -> list[str]:
    """Split markdown content into chunks at logical boundaries."""
    chunks = []
    lines = text.split('\n')
    current_chunk = []
    current_size = 0

    for line in lines:
        line_size = len(line) + 1  # +1 for newline

        # If adding this line would exceed max_chars and we have content
        if current_size + line_size > max_chars and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_size = line_size
        else:
            current_chunk.append(line)
            current_size += line_size

    # Add remaining content
    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks

def translate_text(text: str) -> str:
    """Translate text using backend API."""
    try:
        print(f"  Sending {len(text)} characters to translation API...")
        response = requests.post(TRANSLATE_URL, json={
            "content": text,
            "target_language": "ur",
            "source_language": "en",
            "use_cache": True
        }, timeout=300)  # 5 minute timeout for large files

        if response.status_code == 200:
            translated = response.json()['translated_content']
            print(f"  ✓ Received {len(translated)} characters")
            return translated
        else:
            print(f"  ERROR: API returned {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"  ERROR: {str(e)}")
        return None

def translate_large_text(text: str) -> str:
    """Translate large text by splitting into chunks."""
    MAX_CHUNK_SIZE = 9000  # Leave some margin under 10000 limit

    if len(text) <= MAX_CHUNK_SIZE:
        return translate_text(text)

    # Split into chunks
    print(f"  File is large ({len(text)} chars), splitting into chunks...")
    chunks = split_markdown(text, MAX_CHUNK_SIZE)
    print(f"  Created {len(chunks)} chunks")

    # Translate each chunk
    translated_chunks = []
    for i, chunk in enumerate(chunks, 1):
        print(f"\n  Chunk {i}/{len(chunks)} ({len(chunk)} chars):")
        translated = translate_text(chunk)
        if not translated:
            print(f"  Failed to translate chunk {i}")
            return None
        translated_chunks.append(translated)

        # Small delay between chunks
        if i < len(chunks):
            time.sleep(1)

    # Combine chunks
    return '\n'.join(translated_chunks)

def main():
    """Main entry point."""
    print("=" * 70)
    print("TRANSLATING MODULE 1 - WEEK 4 (URDF) TO URDU")
    print("=" * 70)

    # Check if source file exists
    if not SOURCE_FILE.exists():
        print(f"\n✗ ERROR: Source file not found: {SOURCE_FILE}")
        return 1

    print(f"\nSource: {SOURCE_FILE}")
    print(f"Output: {OUTPUT_FILE}")

    # Read source file
    print("\n[1/3] Reading source file...")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"  ✓ Read {len(content)} characters")

    # Translate
    print("\n[2/3] Translating to Urdu...")
    translated_content = translate_large_text(content)

    if not translated_content:
        print("\n✗ Translation failed!")
        return 1

    # Save
    print("\n[3/3] Saving translated file...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(translated_content)
    print(f"  ✓ Saved to: {OUTPUT_FILE}")

    print("\n" + "=" * 70)
    print("✓ MODULE 1 TRANSLATION COMPLETE!")
    print("=" * 70)
    print("\nAll Module 1 files are now translated to Urdu:")
    print("  ✓ week1-intro.md")
    print("  ✓ week2-fundamentals.md")
    print("  ✓ week3-python.md")
    print("  ✓ week4-urdf.md (just completed)")

    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
