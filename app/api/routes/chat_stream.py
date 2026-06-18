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


def _friendly_error(exc):

    """Map an exception raised mid-generation to a user-facing message."""

    name = type(exc).__name__

    if "RateLimit" in name or "429" in str(exc):

        return (
            "The language model's usage limit has been reached. "
            "Please wait a few minutes and try again, or upgrade the "
            "model provider plan."
        )

    return (
        "Sorry — something went wrong while generating the answer. "
        "Please try again."
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

        try:

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

        except Exception as exc:  # noqa: BLE001

            # The LLM (or retrieval) failed mid-stream. Rather than crash
            # the SSE response with a 500 and leave the UI hanging, emit a
            # clean error event the client can render, then close the
            # stream gracefully. Rate limits are the common case, so give
            # the user an actionable message.
            message = _friendly_error(exc)

            yield (
                "data: "
                + json.dumps(
                    {"type": "error", "data": message}
                )
                + "\n\n"
            )

            yield (
                "data: "
                + json.dumps({"type": "done"})
                + "\n\n"
            )

            return

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