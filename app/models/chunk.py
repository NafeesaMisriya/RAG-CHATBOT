from dataclasses import dataclass,field

@dataclass
class Chunk:
    chunk_id: str

    node_id: str

    content: str

    page: int

    source_document: str

    metadata: dict=field(default_factory=dict)
