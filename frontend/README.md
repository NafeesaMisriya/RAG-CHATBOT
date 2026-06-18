# DocuMind — React Frontend

A professional, product-grade UI for the DocuMind RAG document-intelligence
chatbot. Replaces the Streamlit prototype with a Vite + React + TypeScript
single-page app.

## Features

- **Document library** — list, select, and delete indexed PDFs.
- **Drag-and-drop upload** with live progress and ingest feedback.
- **Streaming chat** — answers render token-by-token over SSE, with a stop control.
- **Grounded citations** — collapsible source panel with clickable links that
  open the exact PDF page.
- **Retrieved figures** — image gallery with a zoom lightbox.
- **Per-document memory** — each document keeps its own session and history,
  persisted across reloads (localStorage).
- **Markdown answers** (tables, lists, code) via `react-markdown`.
- **Light / dark theme**, responsive layout, and a live backend status indicator.

## Architecture

```
src/
  api/client.ts        REST client + fetch-based SSE streaming reader
  hooks/
    useDocuments.ts    load / refresh the document library
    useChat.ts         per-collection conversations, streaming, persistence
    useTheme.ts        light/dark theme
  components/          Sidebar, DocumentList, UploadPanel, ChatView,
                       MessageBubble, Sources, ImageGallery, Composer, …
  types.ts             shared types mirroring the FastAPI payloads
  App.tsx              app shell wiring it all together
```

## Getting started

1. Start the backend (from the project root):

   ```bash
   uvicorn app.api.main:app --reload --port 8010
   ```

2. Install and run the frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Open http://localhost:5173. The dev server proxies `/api/*` and `/files/*`
   to the backend at `http://127.0.0.1:8010`, so no extra config is needed.

## Production

```bash
npm run build      # outputs static assets to dist/
npm run preview    # serve the production build locally
```

Set `VITE_API_URL` (see `.env.example`) to the deployed API origin when the
frontend and backend are served from different hosts, and add that frontend
origin to the backend's `FRONTEND_ORIGINS` env var (CORS).
