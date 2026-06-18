import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.chat import (
    router as chat_router
)

from app.api.routes.documents import (
    router as documents_router
)
from app.api.routes.upload import (
    router as upload_router
)
from app.api.routes.chat_stream import (
    router as stream_router
)

from app.api.routes.delete_document import (
    router as delete_router
)

from app.api.routes.health import (
    router as health_router
)

app = FastAPI(
    title="DocuMind API",
    version="1.0"
)

# Allow the React frontend (Vite dev server / production build) to call
# the API from a different origin. Override the allowed origins with the
# FRONTEND_ORIGINS env var (comma-separated) in production.
_frontend_origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _frontend_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded PDFs and extracted images so the UI can render
# clickable source links (e.g. /files/uploads/foo.pdf#page=3) and
# image previews (/files/extracted/images/<collection>/<file>).
os.makedirs("data", exist_ok=True)

app.mount(
    "/files",
    StaticFiles(directory="data"),
    name="files"
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

app.include_router(
    stream_router
)

app.include_router(
    delete_router
)

app.include_router(
    health_router
)

@app.get("/")
def home():

    return {
        "message":
        "DocuMind API Running"
    }