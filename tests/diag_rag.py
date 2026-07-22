import sys
from pathlib import Path

# Add project root to path
sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from app.chat.rag_chatbot import RAGChatbot

def diag():
    chatbot = RAGChatbot()
    try:
        print("Calling chatbot.ask('What is DNA?', 'biology_txt')...")
        result = chatbot.ask("What is DNA?", "biology_txt")
        print("Success! Result:")
        print(result)
    except Exception as e:
        print("Error occurred:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diag()
