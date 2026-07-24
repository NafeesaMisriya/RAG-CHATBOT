import os
import google.generativeai as genai

from app.models.vector_record import (
    VectorRecord
)


class EmbeddingManager:

    def __init__(self):
        self.provider = os.environ.get("EMBEDDING_PROVIDER", "local").lower()
        if self.provider == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set")
            genai.configure(api_key=api_key)
        else:
            # Lazy import to prevent loading heavy torch/transformers into memory in cloud
            from sentence_transformers import SentenceTransformer
            self.model = (
                SentenceTransformer(
                    "BAAI/bge-small-en-v1.5"
                )
            )

    def embed_text(
        self,
        text: str
    ):
        if self.provider == "gemini":
            response = genai.embed_content(
                model="models/text-embedding-004",
                contents=text,
                task_type="retrieval_document"
            )
            return response['embedding']
        else:
            vector = (
                self.model.encode(
                    text,
                    normalize_embeddings=True
                )
            )
            return vector.tolist()

    def embed_chunks(
        self,
        chunks
    ):

        vector_records = []

        total = len(chunks)

        for index, chunk in enumerate(
            chunks
        ):

            vector = self.embed_text(
                chunk.content
            )

            record = VectorRecord(
                chunk_id=
                chunk.chunk_id,

                vector=
                vector,

                content=
                chunk.content,

                page=
                chunk.page,

                source_document=
                chunk.source_document,

                metadata=
                chunk.metadata
            )

            vector_records.append(
                record
            )

            if (
                (index + 1) % 25 == 0
                or
                index == total - 1
            ):

                print(
                    f"Embedded "
                    f"{index + 1}/{total}"
                )

        return vector_records