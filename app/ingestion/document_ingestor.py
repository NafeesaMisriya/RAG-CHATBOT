import gc
import os

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
from app.fusion.page_fusion import (
    PageFusion
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
            pdf_path,
            collection_name=
            collection_name
        )

        nodes = parser.parse(
            extract_images=True
        )

        # Free BLIP model from memory before embedding — prevents OOM crash
        # when a large PDF has many image nodes (~500 MB freed here).
        del parser
        gc.collect()

        print(
            f"Nodes: {len(nodes)}"
        )

        fusion = PageFusion()

        image_nodes = [

            node

            for node in nodes

            if node.node_type == "image"
        ]

        non_image_nodes = [

            node

            for node in nodes

            if node.node_type != "image"
        ]

        fused_nodes = (
            fusion.fuse(
                non_image_nodes
            )
        )

        nodes = (
            fused_nodes
            +
            image_nodes
        )

        print(
            f"Fused Nodes: "
            f"{len(nodes)}"
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

        for i, chunk in enumerate(chunks[:10]):
            print("\n===================")
            print(f"Chunk {i}")
            print(chunk.content[:1000])

        print(
            "\nGenerating embeddings..."
        )

        image_chunks = [
            c for c in chunks
            if c.metadata.get("node_type") == "image"
        ]

        print(
            f"\nImage Chunks: "
            f"{len(image_chunks)}"
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
            os.path.basename(pdf_path)
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