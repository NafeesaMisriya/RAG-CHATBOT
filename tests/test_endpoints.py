import json
import requests
import sys
from pathlib import Path

# Add project root to path
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

API_URL = "http://127.0.0.1:8010"

def test_endpoints():
    print("\n--- Verifying Chat API Endpoints ---")
    session_id = "test-session-123"
    collection = "biology_txt"

    # Test Case 1: Conversational query via POST /chat
    print("\n1. Testing /chat with greeting 'Hi'...")
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "question": "Hi",
                "collection_name": collection,
                "session_id": session_id
            },
            timeout=10
        )
        if response.status_code == 200:
            res_data = response.json()
            print("[SUCCESS] Got response:", res_data)
            assert "Hello!" in res_data["answer"]
            assert res_data["sources"] == []
            assert res_data["images"] == []
        else:
            print(f"[FAIL] HTTP Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        print("[FAIL] Connection error:", e)

    # Test Case 2: Conversational query via POST /chat/stream
    print("\n2. Testing /chat/stream with greeting 'Who are you?'...")
    try:
        response = requests.post(
            f"{API_URL}/chat/stream",
            json={
                "question": "Who are you?",
                "collection_name": collection,
                "session_id": session_id
            },
            stream=True,
            timeout=10
        )
        if response.status_code == 200:
            print("[SUCCESS] SSE Stream started:")
            full_answer = ""
            sources = None
            images = None
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        event = json.loads(decoded[6:])
                        if event["type"] == "token":
                            print(event["data"], end="", flush=True)
                            full_answer += event["data"]
                        elif event["type"] == "sources":
                            sources = event["data"]
                        elif event["type"] == "images":
                            images = event["data"]
            print()
            print(f"Final sources: {sources}")
            print(f"Final images: {images}")
            assert "assistant" in full_answer or "ConteXora" in full_answer
            assert sources == []
            assert images == []
        else:
            print(f"[FAIL] HTTP Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        print("[FAIL] Connection error:", e)

    # Test Case 3: Document RAG query via POST /chat/stream
    print("\n3. Testing /chat/stream with RAG query 'What is DNA?' (should stream RAG or return refusal)...")
    try:
        response = requests.post(
            f"{API_URL}/chat/stream",
            json={
                "question": "What is DNA?",
                "collection_name": collection,
                "session_id": session_id
            },
            stream=True,
            timeout=15
        )
        if response.status_code == 200:
            print("[SUCCESS] RAG SSE Stream started:")
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        event = json.loads(decoded[6:])
                        if event["type"] == "token":
                            print(event["data"], end="", flush=True)
                        elif event["type"] == "sources":
                            print(f"\nSources citations: {event['data']}")
                        elif event["type"] == "images":
                            print(f"Image results: {event['data']}")
            print()
        else:
            print(f"[FAIL] HTTP Status: {response.status_code}, Body: {response.text}")
    except Exception as e:
        print("[FAIL] Connection error:", e)

if __name__ == "__main__":
    test_endpoints()
