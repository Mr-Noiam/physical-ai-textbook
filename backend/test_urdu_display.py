"""
Test Urdu translation and create HTML viewer for proper RTL display.

This script creates an HTML file that properly displays Urdu text with
right-to-left (RTL) rendering and connected letters.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TRANSLATE_URL = f"{BASE_URL}/api/v1/translate"

def create_html_viewer(translations):
    """Create HTML file with proper RTL rendering for Urdu."""

    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Urdu Translation Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
        }

        .header {
            background: white;
            padding: 30px;
            border-radius: 15px 15px 0 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .header h1 {
            color: #333;
            font-size: 32px;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 14px;
        }

        .status {
            display: inline-block;
            padding: 5px 15px;
            background: #10b981;
            color: white;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-top: 10px;
        }

        .translations {
            background: white;
            padding: 0;
            border-radius: 0 0 15px 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .translation-card {
            padding: 30px;
            border-bottom: 1px solid #e5e7eb;
        }

        .translation-card:last-child {
            border-bottom: none;
        }

        .english {
            background: #f3f4f6;
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }

        .english-label {
            color: #667eea;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
        }

        .english-text {
            color: #333;
            font-size: 18px;
            line-height: 1.6;
        }

        .urdu {
            background: #fef3c7;
            padding: 20px 25px;
            border-radius: 10px;
            border-right: 4px solid #f59e0b;
            /* RTL support for Urdu */
            direction: rtl;
            text-align: right;
        }

        .urdu-label {
            color: #f59e0b;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
            /* LTR for label */
            direction: ltr;
            text-align: left;
        }

        .urdu-text {
            /* Use fonts that support Urdu properly */
            font-family: 'Jameel Noori Nastaleeq', 'Nafees Web Naskh', 'Noto Nastaliq Urdu', 'Arabic Typesetting', Arial, sans-serif;
            color: #1f2937;
            font-size: 24px;
            line-height: 2;
            font-weight: normal;
            /* Ensure proper text rendering */
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        .metadata {
            display: flex;
            gap: 15px;
            margin-top: 15px;
            font-size: 12px;
            color: #6b7280;
        }

        .metadata span {
            background: #f3f4f6;
            padding: 5px 12px;
            border-radius: 15px;
        }

        .cached {
            background: #10b981 !important;
            color: white;
        }

        .not-cached {
            background: #ef4444 !important;
            color: white;
        }

        .footer {
            text-align: center;
            margin-top: 20px;
            color: white;
            font-size: 14px;
        }

        .explanation {
            background: #fffbeb;
            border: 2px solid #fbbf24;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }

        .explanation h3 {
            color: #f59e0b;
            margin-bottom: 10px;
        }

        .explanation p {
            color: #78350f;
            line-height: 1.6;
        }
    </style>
    <!-- Include Google Fonts for better Urdu support -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 Urdu Translation Viewer</h1>
            <p>Proper RTL (Right-to-Left) rendering with connected letters</p>
            <span class="status">✓ Displaying Correctly</span>
        </div>

        <div class="explanation">
            <h3>Why does Urdu look broken in the terminal?</h3>
            <p>
                <strong>Your terminal doesn't support RTL (right-to-left) text rendering.</strong><br>
                Urdu uses special Unicode characters that need to be connected and displayed right-to-left.
                This HTML viewer uses proper CSS and fonts to display Urdu correctly.
                <br><br>
                <strong>The translation itself is correct</strong> - it's just a display issue in your terminal!
            </p>
        </div>

        <div class="translations">
"""

    # Add each translation
    for i, trans in enumerate(translations, 1):
        cached_class = "cached" if trans.get('cached', False) else "not-cached"
        cached_text = "✓ Cached" if trans.get('cached', False) else "⚡ Fresh Translation"

        html_content += f"""
            <div class="translation-card">
                <div class="english">
                    <div class="english-label">English (Original)</div>
                    <div class="english-text">{trans['original_content']}</div>
                </div>

                <div class="urdu">
                    <div class="urdu-label">اردو (Urdu Translation)</div>
                    <div class="urdu-text">{trans['translated_content']}</div>
                </div>

                <div class="metadata">
                    <span>#{i}</span>
                    <span>{trans['source_language'].upper()} → {trans['target_language'].upper()}</span>
                    <span class="{cached_class}">{cached_text}</span>
                    <span>{trans.get('timestamp', 'N/A')[:19]}</span>
                </div>
            </div>
"""

    html_content += """
        </div>

        <div class="footer">
            <p>Generated with Gemini/OpenAI Translation API</p>
            <p>Urdu text is displayed with proper RTL rendering and font support</p>
        </div>
    </div>
</body>
</html>
"""

    # Write to file
    filename = "urdu_translations_viewer.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    return filename


def test_and_display():
    """Test translations and create HTML viewer."""
    print("=" * 70)
    print("URDU TRANSLATION DISPLAY TEST")
    print("=" * 70)

    # Test phrases
    test_phrases = [
        "Hello, welcome to the robotics course!",
        "Introduction to Robot Operating System",
        "ROS 2 is a flexible framework for writing robot software",
        "Please click here to continue learning",
        "This tutorial covers basic robotics concepts"
    ]

    translations = []

    print("\nTranslating test phrases...")
    for phrase in test_phrases:
        response = requests.post(TRANSLATE_URL, json={
            "content": phrase,
            "target_language": "ur"
        })

        if response.status_code == 200:
            data = response.json()
            translations.append(data)
            status = "[CACHED]" if data['cached'] else "[FRESH]"
            print(f"  {status}: {phrase[:50]}...")
        else:
            print(f"  [ERROR]: {phrase[:50]}...")

    print(f"\nTranslated {len(translations)} phrases")

    # Create HTML viewer
    print("\nCreating HTML viewer with proper RTL rendering...")
    html_file = create_html_viewer(translations)

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)
    print(f"\nCreated: {html_file}")
    print("\nOPEN THIS FILE IN YOUR BROWSER to see Urdu properly!")
    print("\nThe HTML file has:")
    print("  [+] Right-to-left (RTL) text direction")
    print("  [+] Connected Urdu letters (not broken)")
    print("  [+] Proper fonts for Urdu display")
    print("  [+] Beautiful formatting\n")

    # Also save JSON for reference
    with open("urdu_translations_data.json", "w", encoding="utf-8") as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)

    print("Also saved: urdu_translations_data.json (for reference)")

    import os
    import webbrowser

    # Try to open in browser automatically
    try:
        file_path = os.path.abspath(html_file)
        webbrowser.open(f'file:///{file_path}')
        print(f"\nOpening in browser...")
    except:
        print(f"\nManually open: {html_file}")


if __name__ == "__main__":
    try:
        test_and_display()
    except requests.exceptions.ConnectionError:
        print("\nERROR: Backend server not running")
        print("Start with: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
