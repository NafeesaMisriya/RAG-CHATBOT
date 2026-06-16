from app.chat.rag_chatbot import (
    RAGChatbot
)

chatbot = RAGChatbot()

print("\nRAG Chatbot Ready!")
print("Type 'exit' to quit.\n")

while True:

    question = input(
        "\nYou: "
    )

    if (
        question.lower()
        == "exit"
    ):
        break

    result = chatbot.ask(
        question
    )

    print(
    "\nAssistant:\n"
    )

    print(
        result["answer"]
    )

    print(
        "\nSources:\n"
    )

    for source in result["sources"]:

        print(
            f"Document: "
            f"{source['document']}"
        )

        print(
            f"Page: "
            f"{source['page']}"
        )

        print(
            f"Link: "
            f"{source['link']}"
        )

        print(
            "-" * 50
        )