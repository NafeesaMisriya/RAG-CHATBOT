import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)
from app.parsing.pdf_parser import PDFParser

from app.chunking.chunker import Chunker


parser = PDFParser(
    "data/raw/book.pdf"
)

nodes = parser.parse()

chunker = Chunker()

chunks = chunker.chunk_nodes(
    nodes
)

print(
    f"Chunks: {len(chunks)}"
)

print("\n")

print(
    chunks[0]
)