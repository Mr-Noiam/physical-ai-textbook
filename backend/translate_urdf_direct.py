"""Direct translation of week4-urdf.md using Gemini API"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.translation import translate_content
from google import genai

# File paths
SOURCE = Path("../docusaurus/docs/module-1-ros2/week4-urdf.md")
OUTPUT = Path("../docusaurus/i18n/ur/docusaurus-plugin-content-docs/current/module-1-ros2/week4-urdf.md")

def split_content(text, chunk_size=8000):
    """Split text into chunks"""
    lines = text.split('\n')
    chunks = []
    current = []
    size = 0

    for line in lines:
        line_size = len(line) + 1
        if size + line_size > chunk_size and current:
            chunks.append('\n'.join(current))
            current = [line]
            size = line_size
        else:
            current.append(line)
            size += line_size

    if current:
        chunks.append('\n'.join(current))

    return chunks

def translate_with_gemini(text):
    """Direct Gemini API call"""
    from app.config import settings

    client = genai.Client(api_key=settings.gemini_api_key)

    prompt = f"""Translate the following technical documentation from English to Urdu.
Keep code blocks, URLs, and technical terms in English. Only translate the explanatory text.
Use proper Urdu/Arabic words, not English transliterations.

{text}"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt
    )

    return response.text.strip()

# Read source
print("Reading source file...")
content = SOURCE.read_text(encoding='utf-8')
print(f"  {len(content)} characters")

# Split into chunks
print("\nSplitting into chunks...")
chunks = split_content(content, 8000)
print(f"  {len(chunks)} chunks")

# Translate each chunk
translated = []
for i, chunk in enumerate(chunks, 1):
    print(f"\nChunk {i}/{len(chunks)} ({len(chunk)} chars)...")
    result = translate_with_gemini(chunk)
    translated.append(result)
    print(f"  ✓ Done ({len(result)} chars)")

# Combine and save
print("\nCombining and saving...")
final = '\n'.join(translated)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(final, encoding='utf-8')

print(f"\n✓ Complete! Saved to: {OUTPUT}")
print(f"  Total: {len(final)} characters")
