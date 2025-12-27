"""
Simple translation test that writes results to JSON file (avoids Windows encoding issues).
"""

import requests
import json

BASE_URL = "http://localhost:8000"
TRANSLATE_URL = f"{BASE_URL}/api/v1/translate"

def test_all():
    results = {}

    # Test 1: Health check
    print("Testing health check...")
    resp = requests.get(f"{TRANSLATE_URL}/health")
    results["health_check"] = {
        "status_code": resp.status_code,
        "passed": resp.status_code == 200
    }

    # Test 2: Get languages
    print("Testing supported languages...")
    resp = requests.get(f"{TRANSLATE_URL}/languages")
    results["languages"] = {
        "status_code": resp.status_code,
        "passed": resp.status_code == 200,
        "total": resp.json().get("total", 0) if resp.status_code == 200 else 0
    }

    # Test 3: Translate text
    print("Testing translation...")
    resp = requests.post(TRANSLATE_URL, json={
        "content": "ROS 2 is a robotics framework.",
        "target_language": "ur"
    })
    results["translate"] = {
        "status_code": resp.status_code,
        "passed": resp.status_code == 200,
        "cached": resp.json().get("cached", False) if resp.status_code == 200 else None
    }

    # Test 4: Test caching (same request)
    print("Testing cache...")
    resp = requests.post(TRANSLATE_URL, json={
        "content": "ROS 2 is a robotics framework.",
        "target_language": "ur"
    })
    results["cache"] = {
        "status_code": resp.status_code,
        "passed": resp.status_code == 200 and resp.json().get("cached") == True,
        "cached": resp.json().get("cached", False) if resp.status_code == 200 else None
    }

    # Test 5: Multiple translations
    print("Testing multiple translations...")
    resp = requests.post(f"{TRANSLATE_URL}/multiple", json={
        "contents": ["Hello", "World", "Test"],
        "target_language": "ur"
    })
    results["multiple"] = {
        "status_code": resp.status_code,
        "passed": resp.status_code == 200,
        "total": resp.json().get("total", 0) if resp.status_code == 200 else 0
    }

    # Write results to file
    with open("translation_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    for test_name, result in results.items():
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status}: {test_name} (status: {result['status_code']})")

    total_passed = sum(1 for r in results.values() if r["passed"])
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")

    if total_passed == len(results):
        print("\nAll tests passed!")

    return results

if __name__ == "__main__":
    try:
        results = test_all()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend server")
        print("Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"ERROR: {e}")
