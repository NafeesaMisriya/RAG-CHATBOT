import json

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

        for event in (
            chatbot.stream_answer(
                question=
                request.question,

                collection_name=
                request.collection_name,

                history=
                history
            )
        ):

            if event["type"] == "token":

                full_answer += event["data"]

            yield (
                "data: "
                + json.dumps(event)
                + "\n\n"
            )

        # Persist the assistant turn exactly once, after the full
        # answer has streamed. (Previously the client made a second
        # /chat call that regenerated and re-saved the answer, which
        # duplicated history and doubled LLM cost.)
        SessionMemory.add_message(
            request.session_id,
            "assistant",
            full_answer
        )

        yield (
            "data: "
            + json.dumps({"type": "done"})
            + "\n\n"
        )

    return StreamingResponse(
        generate(),
        media_type=
        "text/event-stream"
    )