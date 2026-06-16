from fastapi import APIRouter
from fastapi.responses import StreamingResponse

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
    "/chat/stream"
)
def stream_chat(
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

    def generate():

        full_answer = ""

        for chunk in (
            chatbot.stream_answer(
                question=
                request.question,

                collection_name=
                request.collection_name,

                history=
                history
            )
        ):

            full_answer += chunk

            yield chunk

        SessionMemory.add_message(
            request.session_id,
            "assistant",
            full_answer
        )

    return StreamingResponse(
        generate(),
        media_type=
        "text/plain"
    )