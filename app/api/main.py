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

from fastapi.responses import FileResponse

app.include_router(
    chat_router,
    prefix="/api"
)

app.include_router(
    documents_router,
    prefix="/api"
)

app.include_router(
    upload_router,
    prefix="/api"
)

app.include_router(
    stream_router,
    prefix="/api"
)

app.include_router(
    delete_router,
    prefix="/api"
)

app.include_router(
    health_router,
    prefix="/api"
)

if os.path.exists("frontend/dist"):
    # Serve index.html at root "/"
    @app.get("/")
    def serve_frontend_root():
        return FileResponse("frontend/dist/index.html")

    # Mount static assets
    app.mount(
        "/assets",
        StaticFiles(directory="frontend/dist/assets"),
        name="assets"
    )

    # SPA routing catch-all
    @app.get("/{file_name:path}")
    async def serve_static(file_name: str):
        file_path = os.path.join("frontend/dist", file_name)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse("frontend/dist/index.html")
else:
    @app.get("/")
    def home():
        return {
            "message":
            "DocuMind API Running"
        }