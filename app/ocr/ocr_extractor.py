import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

from PIL import Image


def _is_readable(text: str) -> bool:
    """True when the embedded text layer is real, not OCR garbage.

    Scanned PDFs often carry a corrupt embedded text layer ($ $ $ $ $,
    whitespace, or special-char soup). Length alone is a bad signal —
    those garbage layers are often hundreds of characters long.
    We require that at least 55 % of non-whitespace characters are
    ordinary letters so that `$ # @ \t \x84` pages fall through to
    Tesseract while normal typeset pages are accepted as-is."""

    stripped = text.strip()
    if len(stripped) < 80:
        return False

    non_ws = [c for c in stripped if not c.isspace()]
    if not non_ws:
        return False

    alpha_ratio = sum(1 for c in non_ws if c.isalpha()) / len(non_ws)
    return alpha_ratio >= 0.55


class OCRExtractor:

    def extract_text(
        self,
        page
    ):

        text = page.get_text()

        # Only trust the embedded text layer when it looks like real prose.
        # Scanned PDFs often have a garbage embedded layer ($ $ $ whitespace)
        # that fools a simple length check — _is_readable() filters those out
        # and falls through to Tesseract for proper OCR.
        if _is_readable(text):

            return text

        print(
            "OCR Activated"
        )

        try:

            pix = page.get_pixmap(
                dpi=300
            )

            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            ocr_text = (
                pytesseract.image_to_string(
                    image
                )
            )

            combined_text = (
                text +
                "\n" +
                ocr_text
            )

            return combined_text

        except Exception as e:

            print(
                f"OCR Error: {e}"
            )

            return text

    def extract_image_text(
        self,
        image_path
    ):

        try:

            image = Image.open(image_path)

            # Upscale images smaller than 600 px on the short side.
            # Tesseract accuracy degrades sharply on small images; 2× is a
            # safe minimum and preserves detail better than excessive scaling.
            min_dim = min(image.width, image.height)

            if min_dim < 600:

                scale = max(2.0, 600 / min_dim)

                image = image.resize(
                    (
                        int(image.width * scale),
                        int(image.height * scale)
                    ),
                    Image.LANCZOS
                )

            # Grayscale is faster and slightly more accurate for Tesseract.
            gray = image.convert("L")

            # --psm 11 (sparse text): best for diagrams where labels are
            # scattered rather than laid out in neat paragraphs.
            # --oem 3: use LSTM + legacy engine for best coverage.
            config = "--oem 3 --psm 11"

            ocr_text = pytesseract.image_to_string(
                gray,
                config=config
            )

            return ocr_text.strip()

        except Exception as e:

            print(
                f"Image OCR Error: {e}"
            )

            return ""