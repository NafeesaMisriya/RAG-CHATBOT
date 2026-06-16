from app.parsing.pdf_parser import (
    PDFParser
)

from app.chunking.chunker import (
    Chunker
)

from app.embedding.embedding_manager import (
    EmbeddingManager
)

from app.retrieval.qdrant_manager import (
    QdrantManager
)
from app.utils.document_registry import (
    DocumentRegistry
)


class DocumentIngestor:

    def __init__(self):

        self.chunker = Chunker()

        self.embedder = (
            EmbeddingManager()
        )

        self.qdrant = (
            QdrantManager()
        )

    def ingest(
        self,
        pdf_path: str,
        collection_name: str = "documents"
    ):

        print(
            "\nParsing PDF..."
        )

        parser = PDFParser(
            pdf_path
        )

        nodes = parser.parse(
            extract_images=False
        )

        print(
            f"Nodes: {len(nodes)}"
        )

        print(
            "\nChunking..."
        )

        chunks = (
            self.chunker.chunk_nodes(
                nodes
            )
        )

        print(
            f"Chunks: {len(chunks)}"
        )

        print(
            "\nGenerating embeddings..."
        )

        vector_records = (
            self.embedder.embed_chunks(
                chunks
            )
        )

        print(
            f"Vectors: "
            f"{len(vector_records)}"
        )

        if not vector_records:

            raise ValueError(
                "No vectors generated."
            )

        vector_size = len(
            vector_records[0].vector
        )

        try:

            self.qdrant.create_collection(
                collection_name=
                collection_name,

                vector_size=
                vector_size
            )

        except ValueError:

            pass

        print(
            "\nUploading to Qdrant..."
        )

        self.qdrant.insert_vectors(
            collection_name=
            collection_name,

            vector_records=
            vector_records
        )
        document_name = (
            pdf_path.split("\\")[-1]
        )

        DocumentRegistry.register(
            document_name=
            document_name,

            collection_name=
            collection_name
        )

        print(
            "\nIngestion Complete!"
        )