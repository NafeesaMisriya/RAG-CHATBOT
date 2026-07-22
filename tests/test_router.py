import sys
from pathlib import Path

# Add project root to path
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from app.chat.router import QueryRouter
from app.chat.rag_chatbot import RAGChatbot

def test_router():
    test_cases = {
        # Greetings
        "Hi": ("GENERAL_CHAT", True),
        "Hello": ("GENERAL_CHAT", True),
        "Hey!": ("GENERAL_CHAT", True),
        "Good morning...": ("GENERAL_CHAT", True),
        "Good evening": ("GENERAL_CHAT", True),
        "how are you": ("GENERAL_CHAT", True),
        "how are you doing?": ("GENERAL_CHAT", True),
        "hy": ("GENERAL_CHAT", True),
        "yo": ("GENERAL_CHAT", True),
        
        # Identity
        "Who are you?": ("GENERAL_CHAT", True),
        "What are you?": ("GENERAL_CHAT", True),
        
        # Capabilities
        "What can you do?": ("GENERAL_CHAT", True),
        "Help": ("GENERAL_CHAT", True),
        "How do I use this chatbot?": ("GENERAL_CHAT", True),
        
        # Gratitude
        "Thanks": ("GENERAL_CHAT", True),
        "Thank you": ("GENERAL_CHAT", True),
        
        # Farewells
        "Bye": ("GENERAL_CHAT", True),
        "Goodbye!": ("GENERAL_CHAT", True),
        
        # Document queries (should NOT match)
        "What is DNA?": ("DOCUMENT_QUERY", False),
        "Explain cell division.": ("DOCUMENT_QUERY", False),
        "Hello, can you explain what DNA is?": ("DOCUMENT_QUERY", False), # greeting + query
        "Who are you in terms of biology?": ("DOCUMENT_QUERY", False), # identity word + query
    }

    print("\n--- Running QueryRouter Classification Tests ---")
    failures = 0
    for query, (expected_intent, expected_is_general) in test_cases.items():
        intent, response = QueryRouter.classify_and_respond(query)
        is_general = (intent == "GENERAL_CHAT")
        success = (intent == expected_intent) and (is_general == expected_is_general)
        
        status = "PASSED" if success else "FAILED"
        if not success:
            failures += 1
        
        print(f"[{status}] Query: '{query}' -> Intent: {intent}")
        if is_general:
            print(f"  Response: {response}")

    print(f"\nCompleted: {len(test_cases) - failures}/{len(test_cases)} tests passed.")
    if failures > 0:
        sys.exit(1)

if __name__ == "__main__":
    test_router()
