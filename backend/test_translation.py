"""
Test script for translation API endpoints.

Tests:
1. Get supported languages
2. Translate single text
3. Test caching (same request should be cached)
4. Translate multiple texts
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TRANSLATE_URL = f"{BASE_URL}/api/v1/translate"

def test_supported_languages():
    """Test getting supported languages."""
    print("\n" + "=" * 70)
    print("TEST 1: Get Supported Languages")
    print("=" * 70)

    response = requests.get(f"{TRANSLATE_URL}/languages")

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Total Languages: {data['total']}")
        print("\nSupported Languages:")
        for code, name in list(data['languages'].items())[:5]:
            print(f"  {code}: {name}")
        print("  ...")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_single_translation():
    """Test translating a single text."""
    print("\n" + "=" * 70)
    print("TEST 2: Translate Single Text")
    print("=" * 70)

    payload = {
        "content": "ROS 2 is a flexible framework for writing robot software. It provides tools and libraries for building robotics applications.",
        "target_language": "ur",
        "source_language": "en",
        "use_cache": True
    }

    print(f"Original Text: {payload['content'][:80]}...")
    print(f"Target Language: {payload['target_language']}")

    response = requests.post(TRANSLATE_URL, json=payload)

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Translated Text: {data['translated_content'][:100]}...")
        print(f"Cached: {data['cached']}")
        print(f"Source: {data['source_language']} → Target: {data['target_language']}")
        return data
    else:
        print(f"Error: {response.text}")
        return None


def test_cache():
    """Test that second identical request uses cache."""
    print("\n" + "=" * 70)
    print("TEST 3: Test Caching")
    print("=" * 70)

    payload = {
        "content": "Nodes are independent processes that perform computation in ROS 2.",
        "target_language": "ur",
        "source_language": "en",
        "use_cache": True
    }

    # First request (should not be cached)
    print("First Request (should NOT be cached):")
    response1 = requests.post(TRANSLATE_URL, json=payload)

    if response1.status_code == 200:
        data1 = response1.json()
        print(f"  Cached: {data1['cached']}")
        print(f"  Translation: {data1['translated_content'][:80]}...")
    else:
        print(f"  Error: {response1.text}")
        return False

    # Second request (should be cached)
    print("\nSecond Request (should BE cached):")
    response2 = requests.post(TRANSLATE_URL, json=payload)

    if response2.status_code == 200:
        data2 = response2.json()
        print(f"  Cached: {data2['cached']}")
        print(f"  Translation: {data2['translated_content'][:80]}...")

        # Verify cache worked
        if data2['cached']:
            print("\n✅ Cache is working correctly!")
            return True
        else:
            print("\n⚠️ Warning: Second request was not cached")
            return False
    else:
        print(f"  Error: {response2.text}")
        return False


def test_multiple_translations():
    """Test translating multiple texts."""
    print("\n" + "=" * 70)
    print("TEST 4: Translate Multiple Texts")
    print("=" * 70)

    payload = {
        "contents": [
            "ROS 2 nodes communicate via topics.",
            "Services provide request-response communication.",
            "Actions are used for long-running tasks."
        ],
        "target_language": "ur",
        "source_language": "en"
    }

    print(f"Translating {len(payload['contents'])} texts...")

    response = requests.post(f"{TRANSLATE_URL}/multiple", json=payload)

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data['total']}")
        print(f"Cached: {data['cached_count']}")

        print("\nTranslations:")
        for i, translation in enumerate(data['translations'], 1):
            print(f"\n{i}. Original: {translation['original_content']}")
            print(f"   Translated: {translation['translated_content'][:100]}...")
            print(f"   Cached: {translation['cached']}")

        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_health_check():
    """Test translation API health check."""
    print("\n" + "=" * 70)
    print("TEST 0: Health Check")
    print("=" * 70)

    response = requests.get(f"{TRANSLATE_URL}/health")

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"Service: {data['service']}")
        print(f"Version: {data['version']}")
        print(f"Supported Languages: {data['supported_languages']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("TRANSLATION API TEST SUITE")
    print("=" * 70)
    print(f"Testing endpoint: {TRANSLATE_URL}")

    try:
        # Run tests
        results = []

        # Health check
        results.append(("Health Check", test_health_check()))

        # Get supported languages
        results.append(("Supported Languages", test_supported_languages()))

        # Single translation
        results.append(("Single Translation", test_single_translation() is not None))

        # Cache test
        results.append(("Caching", test_cache()))

        # Multiple translations
        results.append(("Multiple Translations", test_multiple_translations()))

        # Print summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)

        for test_name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {test_name}")

        total_passed = sum(1 for _, passed in results if passed)
        total_tests = len(results)

        print(f"\nTotal: {total_passed}/{total_tests} tests passed")

        if total_passed == total_tests:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️ {total_tests - total_passed} test(s) failed")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to backend server")
        print("Make sure the backend is running:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()
