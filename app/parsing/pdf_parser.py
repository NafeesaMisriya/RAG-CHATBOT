import fitz
import uuid

from pathlib import Path

from app.models.node import Node

from app.ocr.ocr_extractor import (
    OCRExtractor
)
from app.vision.image_captioner import (
    ImageCaptioner
)
from app.parsing.table_extractor import (
    TableExtractor
)


class PDFParser:

    def __init__(
        self,
        pdf_path: str,
        collection_name: str = None,
        image_output_dir: str = None
    ):

        self.pdf_path = pdf_path

        # ----------------------------------------------------------
        # Cross-PDF image isolation:
        # Each document writes its extracted images into a dedicated
        # sub-directory keyed by collection (or the PDF file stem).
        # Without this, files like "page_1_img_0.png" collide across
        # PDFs and a later ingestion overwrites an earlier document's
        # images, so the stored image_path serves the wrong picture.
        # ----------------------------------------------------------

        if image_output_dir is None:

            namespace = (
                collection_name
                if collection_name
                else Path(pdf_path).stem
            )

            image_output_dir = str(
                Path("data/extracted/images")
                / namespace
            )

        self.image_output_dir = (
            image_output_dir
        )

        self.ocr = OCRExtractor()

        self.captioner = (
            ImageCaptioner()
        )
        self.table_extractor = (
            TableExtractor()
        )

        Path(
            self.image_output_dir
        ).mkdir(
            parents=True,
            exist_ok=True
        )

    def _create_text_node(
        self,
        text,
        page_num
    ):

        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        detected_title = None

        detected_unit = None

        for line in lines[:15]:

            if (
                len(line) > 5
                and
                len(line) < 100
            ):

                if (
                    "UNIT" in line.upper()
                ):

                    detected_unit = line

                elif (
                    detected_title is None
                ):

                    detected_title = line

        return Node(
            node_id=str(
                uuid.uuid4()
            ),

            node_type="text",

            page=page_num,

            content=text,

            source_document=
            self.pdf_path,

            unit=
            detected_unit,

            title=
            detected_title
        )

    def _extract_images(
        self,
        doc,
        page,
        page_num
    ):

        image_nodes = []

        image_list = (
            page.get_images()
        )

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

                # -------------------------
                # BLIP CAPTION
                # -------------------------

                caption = (
                    self.captioner
                    .caption_image(
                        str(image_path)
                    )
                )

                print(
                    f"Image Caption: "
                    f"{caption}"
                )

                # -------------------------
                # IMAGE OCR
                # Extract any text embedded
                # inside the figure/diagram
                # so it becomes searchable.
                # -------------------------

                ocr_text = (
                    self.ocr
                    .extract_image_text(
                        str(image_path)
                    )
                )

                if ocr_text:

                    print(
                        f"Image OCR: "
                        f"{ocr_text[:100]}"
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

                    source_document=
                    self.pdf_path,

                    caption=
                    caption,

                    ocr_text=
                    ocr_text
                )

                image_nodes.append(
                    image_node
                )

            except Exception as e:

                print(
                    f"Image extraction error: "
                    f"{e}"
                )

        return image_nodes
    def parse(
        self,
        extract_images=False
    ):

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
                    self.ocr.extract_text(
                        page
                    )
                )

                print(
                    f"Page {page_num}: "
                    f"{len(text)} chars"
                )

                if text.strip():

                    text_node = (
                        self._create_text_node(
                            text,
                            page_num
                        )
                    )

                    nodes.append(
                        text_node
                    )

                table_nodes = (
                    self._extract_tables(
                        page_num
                    )
                )

                nodes.extend(
                    table_nodes
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

    def _extract_tables(
        self,
        page_num
    ):

        table_nodes = []

        tables = (
            self.table_extractor
            .extract_tables(
                self.pdf_path,
                page_num
            )
        )

        for table_text in tables:

            table_nodes.append(
                Node(
                    node_id=str(
                        uuid.uuid4()
                    ),

                    node_type="table",

                    page=page_num,

                    table_data=
                    table_text,

                    source_document=
                    self.pdf_path
                )
            )

        return table_nodes