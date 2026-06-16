from fastapi import FastAPI

from app.api.routes.chat import (
    router as chat_router
)

from app.api.routes.documents import (
    router as documents_router
)
from app.api.routes.upload import (
    router as upload_router
)

app = FastAPI(
    title="DocuMind API",
    version="1.0"
)

app.include_router(
    chat_router
)

app.include_router(
    documents_router
)

app.include_router(
    upload_router
)

@app.get("/")
def home():

    return {
        "message":
        "DocuMind API Running"
    }