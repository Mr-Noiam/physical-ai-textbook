"""Test translating a single file to Urdu"""

import sys
from pathlib import Path
import requests

# Fix Windows console encoding for Unicode/Urdu characters
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

API_BASE_URL = "http://localhost:8000"
TRANSLATE_URL = f"{API_BASE_URL}/api/v1/translate"

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
        }, timeout=30)

        if response.status_code == 200:
            data = response.json()
            return data['translated_content']
        else:
            print(f"ERROR: Translation API returned {response.status_code}")
            return text
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return text

# Test with intro.md
input_file = DOCS_DIR / "intro.md"
output_file = URDU_DOCS_DIR / "intro.md"

print(f"Reading: {input_file}")
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

print(f"Translating {len(main_content)} characters...")

# Translate the main content (not line by line, just the whole thing for test)
translated_content = translate_text(main_content.strip())

# Combine
urdu_content = frontmatter + '\n\n' + translated_content

# Write output
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(urdu_content)

print(f"SUCCESS! Saved to: {output_file}")
print(f"Translated {len(translated_content)} characters")
