import uuid

from llama_index.core.node_parser import (SentenceSplitter)
from app.models.chunk import Chunk

class Chunker:

    def __init__(
        self,
        chunk_size=500,
        chunk_overlap=100
    ):

        self.splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def chunk_node(
        self,
        node
    ):

        if node.node_type != "text":
            return []

        pieces = self.splitter.split_text(
            node.content
        )

        chunks = []

        for piece in pieces:

            chunk = Chunk(
                chunk_id=str(
                    uuid.uuid4()
                ),
                

                node_id=node.node_id,

                content=piece,

                page=node.page,

                source_document=node.source_document,

                metadata={
                    "node_type":
                    node.node_type
                }
            )

            chunks.append(
                chunk
            )

        return chunks

    def chunk_nodes(
        self,
        nodes
    ):

        all_chunks = []
        

        for node in nodes:

            node_chunks = (
                self.chunk_node(
                    node
                )
            )

            all_chunks.extend(
                node_chunks
            )

        return all_chunks