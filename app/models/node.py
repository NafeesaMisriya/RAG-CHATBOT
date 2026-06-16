from dataclasses import dataclass
from typing import Optional


@dataclass
class Node:
    node_id: str
    node_type: str
    page: int

    content: Optional[str] = None

    image_path: Optional[str] = None

    source_document: Optional[str] = None