# DocuMind / RAG Document Intelligence Chatbot

A full-stack Retrieval-Augmented Generation (RAG) application for chatting with PDF documents. Users can upload one or more PDFs, extract text and images, build vector indexes, and ask questions in natural language while receiving grounded answers with source references.

This repository combines:

- a FastAPI backend for ingestion, retrieval, and chat APIs
- a React + Vite frontend for a polished document-chat experience
- an optional Streamlit demo interface for quick local testing
- Qdrant-based vector search with reranking and LLM-based generation

## Why this project exists

The project is designed to make document understanding accessible and practical. Instead of reading large PDFs manually, users can ask questions such as:

- “What does this document say about X?”
- “Summarize the key findings in this PDF.”
- “Show me the relevant figures or diagrams.”
- “What page contains the answer?”

The system uses a modern RAG pipeline to ground answers in the uploaded content rather than relying only on model memorization.

## Key features

- PDF upload and ingestion
- Text extraction and OCR-assisted processing
- Table and image-aware parsing
- Chunking and embedding generation
- Vector similarity search with Qdrant
- Reranking of retrieved passages for better relevance
- LLM-backed answer generation with source-aware responses
- Streaming chat responses for a responsive UI
- Session memory for multi-turn conversations
- Document management and deletion
- Optional image retrieval for relevant figures

## Architecture overview

The project is organized as a layered RAG pipeline:

1. Ingestion layer
   - Parses uploaded PDFs
   - Extracts text, tables, images, and OCR content
   - Builds document nodes and chunks

2. Embedding and retrieval layer
   - Generates vector embeddings for chunks
   - Stores them in Qdrant
   - Retrieves relevant passages for a query
   - Reranks them for improved relevance

3. Generation layer
   - Rewrites the user query when needed
   - Sends context and conversation history to an LLM
   - Returns a grounded answer with references

4. Application layer
   - FastAPI exposes REST and streaming endpoints
   - React frontend provides the main user experience
   - Streamlit provides a lightweight alternative UI

## Project structure

```text
chatbot/
├── app/
│   ├── api/
│   │   ├── main.py
│   │   └── routes/
│   ├── chat/
│   ├── chunking/
│   ├── embedding/
│   ├── generation/
│   ├── ingestion/
│   ├── llm/
│   ├── models/
│   ├── ocr/
│   ├── parsing/
│   ├── query_rewriting/
│   ├── reranking/
│   ├── retrieval/
│   ├── utils/
│   ├── vision/
│   └── workflow/
├── data/
│   ├── uploads/
│   ├── extracted/
│   ├── processed/
│   └── document_registry.json
├── frontend/
│   ├── src/
│   └── package.json
├── tests/
├── requirements.txt
├── streamlit_app.py
└── README.md
```

## Tech stack

### Backend
- Python
- FastAPI
- Uvicorn
- Qdrant client
- LangChain
- sentence-transformers
- PyMuPDF / PDF parsing utilities
- OCR and image processing libraries

### Frontend
- React
- TypeScript
- Vite
- React Markdown

### AI / ML
- Groq or Gemini LLM support
- Embedding models via sentence-transformers
- Optional image captioning and OCR enhancement

## Prerequisites

Before running the project, make sure you have:

- Python 3.10+ installed
- Node.js 18+ and npm installed
- A running Qdrant instance
- A valid LLM API key from either Groq or Google Gemini

## Environment configuration

Create a `.env` file in the project root with values similar to the following:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.3-70b-versatile

# Optional alternative provider
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash

QDRANT_URL=http://127.0.0.1:6333
QDRANT_API_KEY=
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

If you use a different Qdrant host or port, update the URL accordingly.

## Installation

### 1) Create and activate a Python environment

```bash
cd chatbot
python -m venv .venv
source .venv/bin/activate
# On Windows use: .venv\Scripts\activate
```

### 2) Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3) Install frontend dependencies

```bash
cd frontend
npm install
```

## Running the application

### Start Qdrant

If you do not already have Qdrant running, start it locally with Docker:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Start the backend

From the project root:

```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8010
```

The backend will be available at:

- http://127.0.0.1:8010
- API docs: http://127.0.0.1:8010/docs

### Start the frontend

From the frontend directory:

```bash
cd frontend
npm run dev
```

The React UI will be served at:

- http://127.0.0.1:5173

### Optional: Start the Streamlit demo

From the project root:

```bash
streamlit run streamlit_app.py
```

## Usage

1. Open the frontend in your browser.
2. Upload a PDF document.
3. Wait for the ingestion pipeline to finish.
4. Select the document and start asking questions.
5. The app will return an answer and relevant source references.

## API overview

The backend provides the following routes:

- GET /health — health check
- GET /documents — list ingested documents
- POST /upload — upload and ingest a PDF
- POST /chat — standard chat request
- POST /chat/stream — streaming chat response
- DELETE /documents/{collection} — delete a document collection

## Data flow

A typical request goes through the following path:

1. The PDF is uploaded and stored under the data directory.
2. The ingestion pipeline parses the document.
3. Text and image nodes are chunked.
4. Embeddings are generated.
5. Chunks are stored in Qdrant.
6. The user question is embedded and used to retrieve relevant chunks.
7. Retrieved context is reranked and passed to the LLM.
8. The answer is returned to the UI with references.

## Testing

The repository includes a suite of test scripts under the tests directory. These cover ingestion, embeddings, Qdrant operations, parser behavior, and chat-related flows.

Example:

```bash
pytest tests/test_ingestion.py
```

## Notes and limitations

- The quality of retrieval depends heavily on the quality of the source document and the embedding model.
- OCR and image-based extraction may vary depending on the document quality.
- Some features require a working LLM provider and a reachable Qdrant instance.
- The project is actively evolving and may require small adjustments depending on your environment.

## Contributing

Contributions are welcome. If you plan to improve the ingestion pipeline, retrieval strategy, UI, or documentation, please open an issue or submit a pull request.

## License

No license file was found in the repository. If you intend to publish or share this project publicly, add an appropriate open-source license before doing so.
