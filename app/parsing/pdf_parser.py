import fitz
import uuid
from pathlib import Path

from app.models.node import Node


class PDFParser:

    def __init__(
        self,
        pdf_path: str,
        image_output_dir: str = "data/extracted/images"
    ):
        self.pdf_path = pdf_path
        self.image_output_dir = image_output_dir

        Path(
            self.image_output_dir
        ).mkdir(
            parents=True,
            exist_ok=True
        )

    def _create_text_node(
        self,
        text: str,
        page_num: int
    ):

        return Node(
            node_id=str(uuid.uuid4()),
            node_type="text",
            page=page_num,
            content=text,
            source_document=self.pdf_path
        )

    def _extract_images(
        self,
        doc,
        page,
        page_num
    ):

        image_nodes = []

        image_list = page.get_images()

        for img_index, img in enumerate(
            image_list
        ):

            try:

                xref = img[0]

                base_image = (
                    doc.extract_image(
                        xref
                    )
                )

                image_bytes = (
                    base_image["image"]
                )

                image_ext = (
                    base_image["ext"]
                )

                filename = (
                    f"page_{page_num}"
                    f"_img_{img_index}"
                    f".{image_ext}"
                )

                image_path = (
                    Path(
                        self.image_output_dir
                    )
                    / filename
                )

                with open(
                    image_path,
                    "wb"
                ) as img_file:

                    img_file.write(
                        image_bytes
                    )

                image_node = Node(
                    node_id=str(
                        uuid.uuid4()
                    ),
                    node_type="image",
                    page=page_num,
                    image_path=str(
                        image_path
                    ),
                    source_document=self.pdf_path
                )

                image_nodes.append(
                    image_node
                )

            except Exception as e:

                print(
                    f"Image extraction error:"
                    f" {e}"
                )

        return image_nodes

    def parse(self,extract_images=False):

        nodes = []

        doc = fitz.open(
            self.pdf_path
        )

        try:

            for page_index in range(
                len(doc)
            ):

                page = doc[
                    page_index
                ]

                page_num = (
                    page_index + 1
                )

                text = (
                    page.get_text()
                )
                text = (
                    page.get_text()
                )

                print(
                    f"Page {page_num}: "
                    f"{len(text)} chars"
                )

                if text.strip():
                    print(
                        f"Creating text node "
                        f"for page {page_num}"
                    )

                    text_node = (
                        self._create_text_node(
                            text,
                            page_num
                        )
                    )

                    nodes.append(
                        text_node
                    )

                if extract_images:

                    image_nodes = (
                        self._extract_images(
                            doc,
                            page,
                            page_num
                        )
                    )

                    nodes.extend(
                        image_nodes
                    )

        finally:

            doc.close()

        return nodes