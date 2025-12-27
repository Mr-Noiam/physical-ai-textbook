"""
Test improved Urdu translation quality.
"""

import requests
import json

BASE_URL = "http://localhost:8000"
TRANSLATE_URL = f"{BASE_URL}/api/v1/translate"

def test_improved_urdu():
    """Test improved Urdu translations."""
    print("=" * 70)
    print("IMPROVED URDU TRANSLATION TEST")
    print("=" * 70)

    test_phrases = [
        {
            "english": "Hello, welcome to the robotics course!",
            "expected_style": "More formal greeting"
        },
        {
            "english": "Introduction to Robot Operating System",
            "expected_style": "Formal educational title"
        },
        {
            "english": "Please click here to continue",
            "expected_style": "Polite instruction"
        },
        {
            "english": "ROS 2 is a flexible framework for writing robot software",
            "expected_style": "Technical content with proper Urdu"
        }
    ]

    results = []

    for i, test in enumerate(test_phrases, 1):
        print(f"\n{i}. Testing: {test['english']}")
        print(f"   Expected style: {test['expected_style']}")

        # Translate
        response = requests.post(TRANSLATE_URL, json={
            "content": test['english'],
            "target_language": "ur",
            "use_cache": False  # Don't use cache for testing
        })

        if response.status_code == 200:
            data = response.json()
            translated = data['translated_content']

            # Save result
            result = {
                "english": test['english'],
                "urdu": translated,
                "cached": data['cached']
            }
            results.append(result)

            # Display (save to file to avoid encoding issues)
            print(f"   ✓ Translated successfully")
            print(f"   Cached: {data['cached']}")

        else:
            print(f"   ✗ Error: {response.status_code}")
            print(f"   {response.text}")

    # Save all results to JSON file
    with open("improved_urdu_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Translated {len(results)} phrases")
    print("Full results saved to: improved_urdu_results.json")
    print("\nOpen improved_urdu_results.json to see the Urdu translations")
    print("(Urdu text displays better in the JSON file)")

if __name__ == "__main__":
    try:
        test_improved_urdu()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Backend server not running")
        print("Start the server with:")
        print("  python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
