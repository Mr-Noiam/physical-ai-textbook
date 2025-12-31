"""Test script to check chatbot API directly."""
import requests
import json

API_URL = "http://localhost:8000/api/v1/chatbot/ask"

def test_chatbot():
    print("=" * 60)
    print("Testing Chatbot API")
    print("=" * 60)

    # Test question
    question = "How do I create a URDF file?"

    print(f"\nQuestion: {question}")
    print("\nSending request to API...")

    # Send request
    try:
        response = requests.post(
            API_URL,
            json={
                "question": question,
                "selected_text": None,
                "conversation_history": None
            },
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("\n[SUCCESS] Chatbot response:")
            print(f"\nAnswer:\n{data['answer']}\n")

            if data.get('sources'):
                print(f"Sources ({len(data['sources'])}):")
                for i, source in enumerate(data['sources'], 1):
                    print(f"  {i}. {source['section']}")
                    print(f"     File: {source['file']}")
        else:
            print(f"\n[ERROR] Request failed")
            print(f"Response: {response.text}")

    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out after 60 seconds")
    except Exception as e:
        print(f"[ERROR] {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_chatbot()
