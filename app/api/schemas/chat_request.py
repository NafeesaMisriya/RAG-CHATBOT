from pydantic import BaseModel


class ChatRequest(
    BaseModel
):

    question: str

    collection_name: str

    session_id: str="default"