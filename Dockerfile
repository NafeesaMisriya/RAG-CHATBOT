# --- Stage 1: Build the Vite + React frontend ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Run the FastAPI backend & serve frontend static files ---
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (including tesseract-ocr for document processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake model weights into the image layers at build time to prevent downloads on cold starts
RUN python -c "\
from sentence_transformers import SentenceTransformer, CrossEncoder; \
SentenceTransformer('BAAI/bge-small-en-v1.5'); \
CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2'); \
"

# Copy backend code
COPY app/ ./app/
RUN mkdir -p data

# Copy the built frontend static files from Stage 1 into /app/frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port (Cloud Run sets PORT env var, defaults to 8080)
EXPOSE 8080

# Command to run uvicorn (shell form to expand $PORT environment variable)
CMD uvicorn app.api.main:app --host 0.0.0.0 --port $PORT
