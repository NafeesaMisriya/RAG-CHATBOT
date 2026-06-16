from fastapi import APIRouter

from app.chat.rag_chatbot import (
    RAGChatbot
)

from app.chat.session_memory import (
    SessionMemory
)

from app.api.schemas.chat_request import (
    ChatRequest
)

router = APIRouter()

chatbot = (
    RAGChatbot()
)


@router.post(
    "/chat"
)
def chat(
    request: ChatRequest
):

    history = (
        SessionMemory.get_history(
            request.session_id
        )
    )

    SessionMemory.add_message(
        request.session_id,
        "user",
        request.question
    )

    result = chatbot.ask(
        question=
        request.question,

        collection_name=
        request.collection_name,

        history=
        history
    )

    SessionMemory.add_message(
        request.session_id,
        "assistant",
        result["answer"]
    )
    
    return result