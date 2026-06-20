import fitz
import re
import uuid

from collections import Counter
from pathlib import Path

# Matches explicit figure caption lines: "Figure 3.2", "Fig. 1", "Diagram 2.1",
# "Chart 4", "Photo 1", "Illustration 2", "Plate 3", "Image 1".
# Requires word + digit so "figuring" or standalone "figure" don't match.
_CAPTION_RE = re.compile(
    r'^\s*(figure|fig\.?|plate|diagram|chart|photo|illustration|exhibit|image)\s+[\d\.]',
    re.IGNORECASE
)

# BLIP caption substrings that identify decorative page chrome.
# Checked as substring matches so partial phrases still fire.
_DECORATIVE_CAPTIONS = frozenset({
    # Blank / frame elements
    "sticky note", "note paper", "blank paper", "blank page",
    "blank sheet", "white frame", "pink border", "blue border",
    # QR codes / barcodes
    "qr code", "qr - qr",
    # Background / texture / callout box patterns
    "background with a floral", "background with a gry",
    "background with a white background",  # repeating bg = noise texture
    "white sheet with a", "white square frame",
    "yellow frame with", "blank paper with a border",
    "beige background", "wavy background",
    "striped background", "blue and yellow striped",
    "beige paint color", "beige paint",
    "piece of paper with a brown", "piece of paper with a yellow",
    "piece of paper with a blue", "piece of paper with a red",
    "white and gray abstract", "gray abstract pattern",
    "abstract pattern",
    "light blue color with a white", "light blue background",
    "blue color with a white background",
    "color with a white background",
    # Textbook navigation icons
    "girl sitting on a chair", "girl reading a book",
    "boy with a hand up", "drawing of a boy", "computer mouse",
    "girl holding a magni", "girl with a magni",
    "logo for the computer", "logo for the new",
    # People / activity icons (sidebar chrome)
    "boy reading a book", "boy sitting at a",
    "boy with glasses reading", "boy and girl sitting on a bench",
    "girl is playing", "girl sitting at her desk",
    "woman sitting on a bench", "man in a suit",
    "silhouette of a man", "hands raised up",
    "young boy sitting at a desk", "drawing of a man",
    "a black and white drawing of a man",
    # Activity-panel icons
    "looking at a flower", "looking at a plant",
    "notepad with a blank", "chain with a blank", "chain around it",
    # Logo / watermark spam
    "logo for the school", "logo for the world",
    "logo for the department",
    "logo for the indian", "logo for the state",
    "logo for the national", "logo for the government",
})

# Minimum pixel dimension on either side.  Images narrower or shorter than
# this are icons, bullets, horizontal rules, or other page chrome.
_MIN_IMAGE_DIM = 100

# If any word (length > 2) appears this many times in the BLIP caption the
# model is hallucinating on a noise / texture / decorative image — skip it.
_HALLUCINATION_REPEAT = 4

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

    @staticmethod
    def _block_is_readable(block_text: str) -> bool:
        """True when a text block contains real prose, not OCR garbage."""
        stripped = block_text.strip()
        if len(stripped) < 4:
            return False
        non_ws = [c for c in stripped if not c.isspace()]
        if not non_ws:
            return False
        return sum(1 for c in non_ws if c.isalpha()) / len(non_ws) >= 0.40

    @staticmethod
    def _is_decorative_caption(caption: str) -> bool:
        """True when the BLIP caption identifies the image as decorative
        page chrome (icon, sticky note, blank frame, QR code, etc.)."""
        text = (caption or "").lower()
        return any(marker in text for marker in _DECORATIVE_CAPTIONS)

    @staticmethod
    def _is_hallucinated_caption(caption: str) -> bool:
        """True when BLIP is hallucinating: any meaningful word (> 2 chars)
        repeats 4+ times.  This reliably catches captions like
        'a cica cica cica cica' or 'dna dna dna dna dna' that BLIP produces
        when the image is a noise texture, background pattern, or page chrome
        it cannot interpret."""
        words = [
            w for w in (caption or "").lower().split()
            if len(w) > 2
        ]
        if len(words) < _HALLUCINATION_REPEAT:
            return False
        return (
            Counter(words).most_common(1)[0][1]
            >= _HALLUCINATION_REPEAT
        )

    def _find_figure_label(
        self,
        page,
        xref,
        blocks
    ):

        """Return the explicit figure caption line for this image, e.g.
        'Figure 3.2: Structure of the neuron'.  Returns '' when no labelled
        caption is found (decorative or unlabelled images)."""

        try:

            rects = page.get_image_rects(xref)

        except Exception:

            return ""

        if not rects:

            return ""

        rect = rects[0]
        cx = (rect.x0 + rect.x1) / 2
        cy = (rect.y0 + rect.y1) / 2

        def dist(block):

            bx = (block[0] + block[2]) / 2
            by = (block[1] + block[3]) / 2

            return ((bx - cx) ** 2 + (by - cy) ** 2) ** 0.5

        caption_blocks = [
            b for b in (blocks or [])
            if self._block_is_readable(b[4])
            and _CAPTION_RE.match(b[4].strip())
        ]

        if not caption_blocks:

            return ""

        caption_blocks.sort(key=dist)

        return (
            caption_blocks[0][4]
            .strip()
            .replace("\n", " ")
            [:300]
        )

    def _nearest_text(
        self,
        page,
        xref,
        blocks,
        fallback_ocr: str = ""
    ):

        """Return the page text most relevant to this figure for indexing.

        Phase 1 — Explicit figure captions (Figure X.Y, Fig., Diagram …)
        are the strongest retrieval signal; returned directly when found.
        Phase 2 — Short text blocks immediately below the image (≤ 120 pt
        gap, ≤ 400 chars) are used when no labelled caption exists; these
        are typically sub-figure labels or un-numbered descriptions.
        Phase 3 — General nearest-text fallback: 5 closest readable blocks.
        Phase 4 — Page-level Tesseract output for fully scanned pages."""

        try:

            rects = page.get_image_rects(xref)

        except Exception:

            return ""

        if not rects:

            return ""

        rect = rects[0]
        cx = (rect.x0 + rect.x1) / 2
        cy = (rect.y0 + rect.y1) / 2

        def centroid_dist(block):

            bx = (block[0] + block[2]) / 2
            by = (block[1] + block[3]) / 2

            return ((bx - cx) ** 2 + (by - cy) ** 2) ** 0.5

        readable = [
            b for b in (blocks or [])
            if self._block_is_readable(b[4])
        ]

        if not readable:

            return (
                fallback_ocr[:400].strip()
                if fallback_ocr
                else ""
            )

        # Phase 1: explicit figure caption line
        caption_blocks = [
            b for b in readable
            if _CAPTION_RE.match(b[4].strip())
        ]

        if caption_blocks:

            caption_blocks.sort(key=centroid_dist)

            return (
                caption_blocks[0][4]
                .strip()
                .replace("\n", " ")
                [:600]
            )

        # Phase 2: short text directly below the image
        below_blocks = [
            b for b in readable
            if b[1] >= rect.y1 - 5        # top of block at/below image bottom
            and b[1] <= rect.y1 + 120     # within 120 pt gap
            and 10 <= len(b[4].strip()) <= 400  # caption-length, not a full paragraph
        ]

        if below_blocks:

            below_blocks.sort(key=lambda b: b[1])

            text = " ".join(
                b[4].strip().replace("\n", " ")
                for b in below_blocks[:3]
            )

            return text[:600].strip()

        # Phase 3: general nearest text (original behaviour)
        nearest = sorted(readable, key=centroid_dist)[:5]

        text = " ".join(
            block[4].strip().replace("\n", " ")
            for block in nearest
        )

        return text[:600].strip()

    def _extract_images(
        self,
        doc,
        page,
        page_num,
        page_ocr_text: str = ""
    ):

        image_nodes = []

        image_list = (
            page.get_images(full=True)
        )

        # Text blocks on the page, used to attach each figure's nearby
        # caption/label text (computed once per page).
        try:

            text_blocks = [
                block
                for block in page.get_text("blocks")
                if block[6] == 0 and block[4].strip()
            ]

        except Exception:

            text_blocks = []

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

                # -------------------------
                # GATE 1: SIZE
                # Skip tiny images before
                # writing anything to disk.
                # -------------------------

                img_w = base_image.get("width", 0)
                img_h = base_image.get("height", 0)

                if (
                    img_w < _MIN_IMAGE_DIM
                    or img_h < _MIN_IMAGE_DIM
                ):

                    print(
                        f"  Skipping small image "
                        f"{img_w}x{img_h} px "
                        f"(decorative)"
                    )

                    continue

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

                safe_caption = caption.encode(
                    "ascii", errors="replace"
                ).decode("ascii")

                print(
                    f"Image Caption: "
                    f"{safe_caption}"
                )

                # -------------------------
                # GATE 2: CAPTION
                # Remove saved file and skip
                # decorative page chrome.
                # -------------------------

                if (
                    self._is_decorative_caption(caption)
                    or self._is_hallucinated_caption(caption)
                ):

                    reason = (
                        "hallucinated"
                        if self._is_hallucinated_caption(caption)
                        else "decorative"
                    )

                    print(
                        f"  Skipping {reason} "
                        f"image: {safe_caption[:80]}"
                    )

                    try:

                        image_path.unlink(
                            missing_ok=True
                        )

                    except Exception:

                        pass

                    continue

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

                    safe_ocr = ocr_text[:100].encode(
                        "ascii", errors="replace"
                    ).decode("ascii")

                    print(
                        f"Image OCR: "
                        f"{safe_ocr}"
                    )

                # Explicit caption line, e.g. "Figure 3.2: The neuron"
                figure_label = self._find_figure_label(
                    page,
                    xref,
                    text_blocks
                )

                if figure_label:

                    safe_label = figure_label[:100].encode(
                        "ascii", errors="replace"
                    ).decode("ascii")

                    print(
                        f"Figure Label: {safe_label}"
                    )

                # Broader context text from the page near the figure.
                context_text = self._nearest_text(
                    page,
                    xref,
                    text_blocks,
                    fallback_ocr=page_ocr_text
                )

                if context_text:

                    safe = context_text[:100].encode(
                        "ascii", errors="replace"
                    ).decode("ascii")

                    print(
                        f"Figure Context: {safe}"
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
                    ocr_text,

                    context_text=
                    context_text,

                    figure_label=
                    figure_label
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
                            page_num,
                            page_ocr_text=text
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