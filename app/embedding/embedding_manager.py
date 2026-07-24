from sentence_transformers import (
    SentenceTransformer
)

from app.models.vector_record import (
    VectorRecord
)


class EmbeddingManager:

    def __init__(self):

        self.model = (
            SentenceTransformer(
                "BAAI/bge-small-en-v1.5"
            )
        )

    def embed_text(
        self,
        text: str
    ):

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