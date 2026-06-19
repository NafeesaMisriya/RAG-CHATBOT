import uuid

from llama_index.core.node_parser import (
    SentenceSplitter
)

from app.models.chunk import Chunk


class Chunker:

    def __init__(
        self,
        chunk_size=1000,
        chunk_overlap=200
    ):

        self.splitter = (
            SentenceSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        )

    def chunk_node(
        self,
        node
    ):

        if node.node_type == "image":

            caption = (
                node.caption
                if node.caption
                else ""
            )

            ocr_text = (
                node.ocr_text
                if node.ocr_text
                else ""
            )

            context_text = (
                node.context_text
                if node.context_text
                else ""
            )

            figure_label = (
                node.figure_label
                if node.figure_label
                else ""
            )

            # Build the FIGURE: section.
            # figure_label (explicit caption, e.g. "Figure 3.2: Neurons") is the
            # strongest retrieval signal: it names the topic and figure number.
            # context_text is the broader on-page text near the figure.
            # BLIP caption and OCR follow as secondary signal.
            image_content = ""

            if figure_label:

                image_content += (
                    f"FIGURE: {figure_label}"
                )

                # Append broader context when it adds information beyond the label
                if (
                    context_text
                    and context_text.strip() != figure_label.strip()
                ):

                    image_content += (
                        f" | {context_text}"
                    )

                image_content += "\n"

            elif context_text:

                image_content += (
                    f"FIGURE: {context_text}\n"
                )

            image_content += (
                f"IMAGE CONTENT: {caption}"
            )

            if ocr_text:

                image_content += (
                    f"\nIMAGE TEXT: "
                    f"{ocr_text}"
                )

            return [
                Chunk(
                    chunk_id=str(
                        uuid.uuid4()
                    ),

                    node_id=node.node_id,

                    content=
                    image_content,

                    page=node.page,

                    source_document=
                    node.source_document,

                    metadata={
                        "node_type":
                        "image",

                        "image_path":
                        node.image_path,

                        # figure_label stored as title so the keyword-boost in
                        # Retriever._apply_keyword_boost() matches queries that
                        # reference the figure by number or topic name.
                        "title":
                        figure_label or "",

                        "figure_label":
                        figure_label or ""
                    }
                )
            ]

        if node.node_type != "text":

            return []
        pieces = (
            self.splitter.split_text(
                node.content
            )
        )

        chunks = []

        for piece in pieces:

            metadata_prefix = ""

            if node.unit:

                metadata_prefix += (
                    f"UNIT: "
                    f"{node.unit}\n\n"
                )

            if node.title:

                metadata_prefix += (
                    f"TITLE: "
                    f"{node.title}\n\n"
                )

            metadata_prefix += (
                f"PAGE: "
                f"{node.page}\n\n"
            )

            enriched_content = (
                metadata_prefix
                + piece
            )

            chunk = Chunk(
                chunk_id=str(
                    uuid.uuid4()
                ),

                node_id=node.node_id,

                content=
                enriched_content,

                page=node.page,

                source_document=
                node.source_document,

                metadata={
                    "node_type":
                    node.node_type,

                    "unit":
                    node.unit,

                    "title":
                    node.title
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