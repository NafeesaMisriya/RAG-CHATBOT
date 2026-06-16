from dataclasses import dataclass

@dataclass
class VectorRecord:

    chunk_id: str

    vector: object

    content: str

    page: int

    source_document: str