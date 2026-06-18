import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

from PIL import Image


class OCRExtractor:

    def extract_text(
        self,
        page
    ):

        text = page.get_text()

        # Good digital text page
        if len(text.strip()) > 100:

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

            image = Image.open(
                image_path
            ).convert(
                "RGB"
            )

            ocr_text = (
                pytesseract.image_to_string(
                    image
                )
            )

            return ocr_text.strip()

        except Exception as e:

            print(
                f"Image OCR Error: {e}"
            )

            return ""