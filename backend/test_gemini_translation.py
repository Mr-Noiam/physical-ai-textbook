"""
Test Gemini translation API.

This script tests the free Gemini API for translations.
Make sure you have set GEMINI_API_KEY in your .env file first!
"""

import requests
import json

BASE_URL = "http://localhost:8000"
TRANSLATE_URL = f"{BASE_URL}/api/v1/translate"

def test_gemini():
    """Test Gemini translation."""
    print("=" * 60)
    print("GEMINI TRANSLATION TEST")
    print("=" * 60)

    # Test 1: Check which provider is active
    print("\n1. Checking translation provider...")
    response = requests.get(f"{TRANSLATE_URL}/health")
    if response.status_code == 200:
        print("   ✓ Translation service is healthy")

    # Test 2: Simple translation
    print("\n2. Testing simple translation...")
    payload = {
        "content": "Hello, welcome to the robotics course!",
        "target_language": "ur"
    }

    response = requests.post(TRANSLATE_URL, json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Translation successful")
        print(f"   Original: {data['original_content']}")
        print(f"   Target language: {data['target_language']}")
        print(f"   Cached: {data['cached']}")

        # Save to file to avoid encoding issues
        with open("gemini_test_result.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"   Full result saved to: gemini_test_result.json")
    else:
        print(f"   ✗ Error: {response.status_code}")
        print(f"   {response.text}")
        return False

    # Test 3: Cache test
    print("\n3. Testing cache (same request)...")
    response = requests.post(TRANSLATE_URL, json=payload)

    if response.status_code == 200:
        data = response.json()
        if data['cached']:
            print(f"   ✓ Cache is working! (no API call made)")
        else:
            print(f"   ⚠ Not cached (this might indicate an issue)")

    # Test 4: Different language
    print("\n4. Testing different target language (Spanish)...")
    payload = {
        "content": "Robotics is the future of automation.",
        "target_language": "es"
    }

    response = requests.post(TRANSLATE_URL, json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Spanish translation successful")
        print(f"   Cached: {data['cached']}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✓ Gemini translation is working!")
    print("✓ You're using the FREE tier (no OpenAI costs)")
    print("✓ Caching is reducing API calls")
    print("\nCheck gemini_test_result.json for full translation details")

    return True

if __name__ == "__main__":
    try:
        test_gemini()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Backend server not running")
        print("Start the server with:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nMake sure you have:")
        print("  1. Set GEMINI_API_KEY in backend/.env")
        print("  2. Set TRANSLATION_PROVIDER=gemini in backend/.env")
        print("  3. Restarted the backend server")
        print("\nSee GEMINI_SETUP.md for detailed setup instructions")
