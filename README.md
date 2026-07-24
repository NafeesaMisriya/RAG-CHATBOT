# ConteXora| Transforming context into Intelligence 

 **ConteXora** is a production-grade, full-stack Retrieval-Augmented Generation (RAG) application designed for chatting with PDF documents. Users can upload one or more PDFs, extract text, tables, and images, build vector indexes, and ask natural language questions. The system yields grounded, context-aware answers complete with page-specific source references and image/figure overlays.

This repository integrates:
- A **FastAPI** backend exposing REST and Server-Sent Events (SSE) streaming API endpoints.
- A **React + Vite** frontend styled using a custom CSS variables design system with responsive sidebar navigation, image galleries, source citations, and dark-mode support.
- A layered pipeline featuring OCR, table parsing, page fusion, vector database storage, keyword boosting, query rewriting, cross-encoder reranking, and failover LLM generator strategies.

---

## Key Features & Advanced Design Decisions

### 1. Hybrid Parsing & Table-Aware Extraction
- **Text Layer Reading**: Text extraction uses PyMuPDF (`fitz`).
- **OCR Fallback**: Scanned PDFs frequently carry corrupted text layers (with special character soup or whitespace). Instead of trusting length checks, [OCRExtractor](file:///c:/Users/Admin/Desktop/pro/DocM/RAG-CHATBOT/app/ocr/ocr_extractor.py) calculates the ratio of alphabetic characters. If less than 55% of the characters are alphabetical, the page is passed to Tesseract OCR to perform high-resolution text extraction.
- **Table Extraction**: Tables are isolated using `pdfplumber` via [TableExtractor](file:///c:/Users/Admin/Desktop/pro/DocM/RAG-CHATBOT/app/parsing/table_extractor.py), formatted cleanly, and merged into the page layout.

### 2. Multi-Modal Node Parsing & Page Fusion
- **Page Fusion**: Standard RAG pipelines chunk text, tables, and images independently, fracturing context. [PageFusion](file:///c:/Users/Admin/Desktop/pro/DocM/RAG-CHATBOT/app/fusion/page_fusion.py) maps text blocks, captions, and tables page by page into a consolidated text node per page, preserving tabular structures alongside standard prose.
- **Image Extraction & Cleaning**: Images are saved in isolation per collection under `data/extracted/images/`. A custom noise filter drops decorative image chrome (watermarks, logos, empty frames) and avoids Salesforce BLIP caption hallucinations by checking word frequency repetition counts.

### 3. Smart Document Chunking
- [Chunker](file:///c:/Users/Admin/Desktop/pro/DocM/RAG-CHATBOT/app/chunking/chunker.py) uses LlamaIndex's `SentenceSplitter` to divide consolidated page content.
- Every text chunk is automatically enriched with structural metadata headers:
  ```text
  UNIT: <unit_name>
  TITLE: <chapter/document_title>
  PAGE: <page_number>

  <chunk_text>
  ```
  This guarantees that even small chunks retrieved out-of-context remain anchored to their origin.

### 4. Dense Embeddings & Vector Indexing
- **Dense Vectors**: Chunks are processed via [EmbeddingManager](file:///c:/Users/Admin/Desktop/pro/DocM/RAG-CHATBOT/app/embedding/embedding_manager.py) using the `BAAI/bge-small-en-v1.5` sentence-transformer model (384 dimensions) with cosine distance.
- **Vector Storage**: [QdrantManager](file:///c:/Users/Admin/Desktop/pro/DocM/RAG-CHATBOT/app/retrieval/qdrant_manager.py) verifies collection constraints and configures custom payload indices on `metadata.node_type` and `page` to allow fast metadata queries and filtering.

### 5. Advanced Two-Stage Retrieval
- **Keyword Boosting**: [Retriever](file:///c:/Users/Admin/Desktop/pro/DocM/RAG-CHATBOT/app/retrieval/retriever.py) applies an exact keyword match boost to retrieved scores. Words matching the user query inside metadata titles receive a high boost (+5), unit names receive (+2), and content matches receive (+0.5).
- **Cross-Encoder Reranking**: The top 100 vector-matched documents are routed to [Reranker](file:///c:/Users/Admin/Desktop/pro/DocM/RAG-CHATBOT/app/reranking/reranker.py) which evaluates contextual alignment using the `cross-encoder/ms-marco-MiniLM-L-12-v2` cross-encoder.

### 6. Relative Grounding Gate
- Absolute cross-encoder scores vary drastically between clean text (around `0` when relevant) and noisy OCR output (scoring deeply negative even when highly relevant).
- Instead of using a hardcoded floor, [RAGChatbot](file:///c:/Users/Admin/Desktop/pro/DocM/RAG-CHATBOT/app/chat/rag_chatbot.py) uses a relative signal (`GROUNDING_GAP = 1.5`): if the spread between the best and worst retrieved matches is smaller than `1.5`, the query is flagged as off-topic or ungrounded. This prevents the model from generating hallucinations for irrelevant questions.

### 7. Page-Joined Image Retrieval
- Image captions are generally too thin to surface reliably through raw vector search (e.g. search queries fail to match "Fig 3.2: human brain diagram").
- To solve this, DocuMind locates figures by page location. The engine identifies which pages the top reranked text answers reside on, pulls all image nodes existing on those specific pages from Qdrant, and runs the cross-encoder to rerank their context, captions, and OCR texts. Only the relevant figures matching the query are selected; others are filtered out.

### 8. Context-Aware Query Rewriting
- [QueryRewriter](file:///c:/Users/Admin/Desktop/pro/DocM/RAG-CHATBOT/app/query_rewriting/query_rewriter.py) uses LLMs to parse multi-turn chat history. Vague follow-up questions referencing pronouns (e.g., *"What about its structure?"* following a question on DNA) are automatically rewritten into fully standalone retrieval questions (*"Explain the structure of DNA"*).

### 9. Multi-LLM Provider Fallbacks
- [LLMFactory](file:///c:/Users/Admin/Desktop/pro/DocM/RAG-CHATBOT/app/llm/llm_factory.py) supports both **Google Gemini** (via `google-generativeai` and `langchain-google-genai`) and **Groq** (via `groq` and `langchain-groq`).
- The application automatically pings the primary LLM provider at startup. If it is rate-limited or fails during generation, the pipeline triggers a failover strategy to route calls to the alternative provider seamlessly.

---

## Project Structure

The codebase is organized as follows:

```text
RAG-CHATBOT/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py             # Standard chat JSON endpoint
│   │   │   ├── chat_stream.py      # Server-Sent Events (SSE) streaming chat endpoint
│   │   │   ├── delete_document.py  # Deletes document registries and vector collection
│   │   │   ├── documents.py        # Lists all uploaded documents
│   │   │   ├── health.py           # API health status check
│   │   │   └── upload.py           # Ingestion initiator for uploaded PDFs
│   │   ├── schemas/
│   │   │   └── chat_request.py     # Pydantic schemas for request validation
│   │   └── main.py                 # FastAPI application setup and routing
│   ├── chat/
│   │   ├── memory.py               # Volatile in-memory chat message store
│   │   ├── rag_chatbot.py          # Orchestrates retrieval, reranking, rewriting, and fallback LLMs
│   │   └── session_memory.py       # Session-keyed multi-turn chat memory
│   ├── chunking/
│   │   └── chunker.py              # Sentence splitting and metadata header enrichment
│   ├── embedding/
│   │   └── embedding_manager.py    # Dense vector generation via BAAI/bge-small-en-v1.5
│   ├── fusion/
│   │   └── page_fusion.py          # Merges text, table extracts, and captions per page
│   ├── generation/
│   │   └── generator.py            # Chat prompts and alternate LLM chains
│   ├── ingestion/
│   │   └── document_ingestor.py    # Pipeline runner orchestrating parser, chunker, embedder, and Qdrant insertion
│   ├── llm/
│   │   ├── gemini_client.py        # Placeholder client file
│   │   └── llm_factory.py          # LLM creator and failover validator (Gemini / Groq)
│   ├── models/
│   │   ├── chunk.py                # Data class representing a processed content chunk
│   │   ├── node.py                 # Data class representing parsed parser units (text, image, table)
│   │   └── vector_record.py        # Data class encapsulating embedded records for Qdrant
│   ├── ocr/
│   │   └── ocr_extractor.py        # Pytesseract OCR layer and image-text extraction
│   ├── parsing/
│   │   ├── pdf_parser.py           # Ingestion layer, PyMuPDF engine, and caption isolation
│   │   └── table_extractor.py      # Pdfplumber interface for table parsing
│   ├── query_rewriting/
│   │   └── query_rewriter.py       # Conversational pronoun resolver and re-writer
│   ├── reranking/
│   │   └── reranker.py             # Re-scores retrieved documents via ms-marco MiniLM
│   ├── retrieval/
│   │   ├── qdrant_manager.py       # Index management and scroll API wrapper
│   │   └── retriever.py            # Similarity searching and keyword boosting
│   ├── utils/
│   │   └── document_registry.py    # Standard JSON document collection registry
│   └── vision/
│       └── image_captioner.py      # Image caption generation (Salesforce BLIP local vs. Gemini vision cloud)
├── data/
│   ├── uploads/                    # Stores original uploaded PDF files
│   ├── extracted/images/           # Extracted image assets organized by collection
│   └── document_registry.json      # Maps document names to collection IDs
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts           # Fetch wrappers and SSE streaming handlers
│   │   ├── components/
│   │   │   ├── ChatView.tsx        # Chat window, streams rendering, and sources toggle
│   │   │   ├── Composer.tsx        # Message input area with submit triggers
│   │   │   ├── DocumentList.tsx    # Upload panel and collections side-panel list
│   │   │   ├── EmptyState.tsx      # Default prompt guidance display
│   │   │   ├── icons.tsx           # Scalable SVG icons UI pack
│   │   │   ├── ImageGallery.tsx    # Renders relevant figures with zoomed modal details
│   │   │   ├── MessageBubble.tsx   # Formatting for user, system, and chatbot messages (ReactMarkdown)
│   │   │   ├── Sidebar.tsx         # Collapsible panel displaying active files
│   │   │   ├── Sources.tsx         # Citation drawer with clickable page hyperlinks
│   │   │   └── UploadPanel.tsx     # File drag-and-drop ingestion container
│   │   ├── hooks/
│   │   │   ├── useChat.ts          # State controller for messages, streams, and active endpoints
│   │   │   ├── useDocuments.ts     # State management for file uploads and deletes
│   │   │   └── useTheme.ts         # Handles local storage based light/dark theme switches
│   │   ├── App.tsx                 # Core UI component layout
│   │   ├── index.css               # Vanilla CSS design system variables and layout rules
│   │   ├── main.tsx                # React app root render
│   │   ├── types.ts                # TypeScript type declarations
│   │   └── vite-env.d.ts           # Vite TypeScript declarations
│   ├── package.json                # Frontend package scripts and dependencies
│   └── vite.config.ts              # Vite configurations
├── tests/                          # Test suites for backend components (Pytest framework)
├── .env                            # Application configuration variables
├── requirements.txt                # Python backend dependencies
└── README.md                       # Comprehensive documentation
```

---

## Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI / Uvicorn** for low-latency async API serving and Server-Sent Events (SSE).
- **Qdrant Python Client** for vector database integration.
- **LangChain & LangChain-Core** for LLM orchestration and chain templates.
- **Sentence-Transformers** for running local embedding (`BAAI/bge-small-en-v1.5`) and reranking (`cross-encoder/ms-marco-MiniLM-L-12-v2`) models.
- **PyMuPDF (fitz)** & **pdfplumber** for page layouts, vector graphics, and tabular parsing.
- **Pytesseract (Tesseract OCR)** for robust optical character recognition on scanned content.
- **Salesforce BLIP** (transformers) as a local, offline image captioning fallback.

### Frontend
- **React 18** (Vite framework) with **TypeScript**.
- **Vanilla CSS** with CSS custom properties (design system) supporting sleek dark and light themes, transitions, animations, and responsive layouts.
- **React Markdown** & **Remark GFM** for formatting mathematical lists, code, and table responses.

---

## Prerequisites

Ensure the following runtimes are installed on your machine:
1. **Python 3.10+** (check with `python --version`).
2. **Node.js 18+** & `npm` (check with `node --version`).
3. **Qdrant DB**: Running locally or via Qdrant Cloud.
4. **Tesseract OCR Engine**:
   - **Windows**: Install Tesseract from UB Mannheim. Ensure it is installed at `C:\Program Files\Tesseract-OCR\tesseract.exe` (which matches the hardcoded path in [ocr_extractor.py](file:///c:/Users/Admin/Desktop/pro/DocM/RAG-CHATBOT/app/ocr/ocr_extractor.py)).
   - **Linux**: Install via `sudo apt-get install tesseract-ocr`.
   - **macOS**: Install via `brew install tesseract`.

---

## Environment Configuration

Create a `.env` file in the project root:

```env
# LLM Providers Configuration
# Supported options: 'groq' or 'gemini'
LLM_PROVIDER=gemini

# Google Gemini Credentials & Models
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_REWRITE_MODEL=gemini-2.5-flash-lite

# Groq Credentials & Models
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_REWRITE_MODEL=llama-3.1-8b-instant

# Captioning Engine Configurations
# Supported options: 'gemini' (cloud, recommended) or 'blip' (local offline BLIP)
CAPTION_PROVIDER=gemini
GEMINI_CAPTION_MODEL=gemini-2.0-flash
GEMINI_CAPTION_DELAY=4.0
BLIP_MODEL=Salesforce/blip-image-captioning-base

# Vector Database Credentials
QDRANT_URL=http://127.0.0.1:6333
QDRANT_API_KEY=

# CORS Configuration
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

## Installation & Setup

### 1. Setup Python Virtual Environment (Backend)
Open a terminal in the root directory:
```bash
python -m venv venv
# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# On macOS / Linux
source venv/bin/activate
```

Install backend dependencies:
```bash
pip install -r requirements.txt
```

### 2. Setup React UI (Frontend)
Navigate into the frontend directory and install NPM packages:
```bash
cd frontend
npm install
```

---

## Running the Application

### 1. Run Qdrant Vector DB
If using a local Docker setup, start Qdrant:
```bash
docker run -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

### 2. Start FastAPI Server
From the root directory (ensure your virtual environment is active):
```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8010
```
- API Endpoint: `http://127.0.0.1:8010`
- Interactive Swagger Documentation: `http://127.0.0.1:8010/docs`

### 3. Start Frontend Development Server
From the `frontend` directory:
```bash
npm run dev
```
Open your browser at: `http://127.0.0.1:5173`


---

## API Documentation

FastAPI exposes the following endpoint routing tables:

### Ingestion & Documents
- **`GET /health`**
  - Returns API health status.
- **`GET /documents`**
  - Returns a JSON list of all registered documents in the registry: `[{"name": "Biology_Notes.pdf", "collection": "biology_notes"}]`.
- **`POST /upload`**
  - Multi-part form request accepting a single `.pdf` file. Parses text, tables, and images, generates embeddings, uploads to Qdrant, registers the collection, and returns metadata.
- **`DELETE /documents/{collection}`**
  - Removes the file metadata from the document registry and drops the Qdrant vector collection.

### Retrieval & Generation Chat
- **`POST /chat`**
  - Standard JSON chat request.
  - Body:
    ```json
    {
      "message": "Explain the cell division process.",
      "collection": "biology_notes",
      "session_id": "optional-uuid-string"
    }
    ```
  - Returns the full grounded response, lists of sources, and relevant figure URLs.
- **`POST /chat/stream`**
  - Streams conversational answers using Server-Sent Events (SSE).
  - Yields token chunks progressively followed by final structured blocks containing citations and figure links (`{"type": "token", "data": "..."}`, `{"type": "sources", "data": [...]}`).

---

## Test Suites

The repository contains automated unit and integration tests located under the `tests/` directory.

To run the full suite:
```bash
pytest
```

Key test files include:
- **`tests/test_parser.py`**: Validates PyMuPDF parser structures, page extraction, and text logic.
- **`tests/test_chunker.py`**: Verifies chunk length constraints, sentence segmentation, and metadata header prefixes.
- **`tests/test_embeddings.py`**: Tests dense embedding dimensionality and vector generation.
- **`tests/test_qdrant.py`**: Assures database connection, upserting records, and search matching functionality.
- **`tests/test_retriever.py`**: Assures that Retriever filters properly and applies query keyword boosting.
- **`tests/test_reranker.py`**: Validates Cross-Encoder output scoring.
- **`tests/test_generator.py`**: Checks answer generation prompts and LLM provider fallbacks.
- **`tests/test_chatbot.py`**: Verifies end-to-end question answering pipeline integrity.
- **`tests/test_gemini.py`**: Exercises Gemini vision captioning prompts and connection logic.
- **`tests/test_langchain.py`**: Tests LangChain wrappers.
- **`tests/verify_reingest.py`**: Validates PDF document re-ingestion steps.
