from app.parsing.pdf_parser import PDFParser
from app.chunking.chunker import Chunker
from app.embedding.embedding_manager import EmbeddingManager

parser = PDFParser(
    "data/raw/Biology.pdf"
)

nodes = parser.parse(extract_images=False)
print(f"Nodes: {len(nodes)}")

if nodes:
    print(nodes[0])


chunker = Chunker()

chunks = chunker.chunk_nodes(
    nodes
)

print(f"Chunks: {len(chunks)}")

embedding_manager = EmbeddingManager()

vector_records = (
    embedding_manager.embed_chunks(
        chunks
    )
)

print(f"Vector Records: {len(vector_records)}")

if vector_records:

    print(vector_records[0])

    print(
        len(
            vector_records[0].vector
        )
    )