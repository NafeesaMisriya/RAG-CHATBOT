import os
import time

from dotenv import load_dotenv
from PIL import Image

load_dotenv()


# Prompt used for cloud captioning. Tuned for figure RETRIEVAL: we want a
# concise, content-bearing description that names the subject and any
# labelled parts, so a student's query matches the right figure.
_CAPTION_PROMPT = (
    "You are labelling a figure extracted from an educational textbook so "
    "it can be found by search. In ONE concise sentence, describe what the "
    "figure shows: name the main subject and any labelled parts, structures, "
    "or steps visible. If the figure contains text labels, include the "
    "important ones. Do not begin with 'This image shows' or 'The figure'. "
    "If the image is decorative or has no meaningful content, reply exactly: "
    "decorative."
)


def _mime_for(path):

    ext = os.path.splitext(path)[1].lower().lstrip(".")

    if ext in ("jpg", "jpeg"):
        return "image/jpeg"

    if ext == "png":
        return "image/png"

    if ext == "webp":
        return "image/webp"

    return "image/jpeg"


class ImageCaptioner:

    """Captions figures at ingest time.

    Backend is selected by the CAPTION_PROVIDER env var:
      - "gemini": Google Gemini vision (cloud, no local RAM, best captions).
                  Requires GEMINI_API_KEY.
      - "blip"  : local Salesforce BLIP (default, offline, weak captions).

    Gemini mode never loads BLIP, which keeps memory use low; on a Gemini
    failure it degrades gracefully (returns "") so ingestion never crashes.
    """

    _processor = None
    _model = None
    _gemini = None

    def __init__(self):

        self.provider = os.getenv(
            "CAPTION_PROVIDER",
            "blip"
        ).strip().lower()

        if self.provider == "gemini":

            self._init_gemini()

        else:

            self._init_blip()

    # ------------------------------------------------------------------
    # Gemini (cloud)
    # ------------------------------------------------------------------

    def _init_gemini(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:

            print(
                "CAPTION_PROVIDER=gemini but GEMINI_API_KEY is not set; "
                "falling back to local BLIP."
            )

            self.provider = "blip"

            self._init_blip()

            return

        self.gemini_model = os.getenv(
            "GEMINI_CAPTION_MODEL",
            "gemini-2.0-flash"
        )

        # Seconds to wait between calls to respect the free-tier rate limit
        # (~15 requests/min for flash). Override with GEMINI_CAPTION_DELAY.
        self.gemini_delay = float(
            os.getenv("GEMINI_CAPTION_DELAY", "4")
        )

        if ImageCaptioner._gemini is None:

            from google import genai

            print(
                f"Using Gemini captioner ({self.gemini_model})..."
            )

            ImageCaptioner._gemini = genai.Client(
                api_key=api_key
            )

    def _caption_gemini(self, image_path):

        from google.genai import types

        with open(image_path, "rb") as f:

            image_bytes = f.read()

        part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=_mime_for(image_path)
        )

        # Retry with backoff on rate-limit / transient errors.
        attempts = 4

        for attempt in range(attempts):

            try:

                response = (
                    ImageCaptioner._gemini
                    .models.generate_content(
                        model=self.gemini_model,
                        contents=[part, _CAPTION_PROMPT]
                    )
                )

                text = (response.text or "").strip()

                # Space out calls so we stay under the per-minute quota.
                if self.gemini_delay > 0:
                    time.sleep(self.gemini_delay)

                if text.lower() == "decorative":
                    return ""

                return text

            except Exception as e:  # noqa: BLE001

                message = str(e).lower()

                rate_limited = (
                    "429" in message
                    or "resource_exhausted" in message
                    or "rate" in message
                    or "quota" in message
                )

                if rate_limited and attempt < attempts - 1:

                    wait = 10 * (attempt + 1)

                    print(
                        f"Gemini rate-limited; retrying in {wait}s "
                        f"(attempt {attempt + 1}/{attempts})"
                    )

                    time.sleep(wait)

                    continue

                print(f"Gemini caption error: {e}")

                return ""

        return ""

    # ------------------------------------------------------------------
    # BLIP (local fallback)
    # ------------------------------------------------------------------

    def _init_blip(self):

        from transformers import (
            BlipProcessor,
            BlipForConditionalGeneration
        )

        model_name = os.getenv(
            "BLIP_MODEL",
            "Salesforce/blip-image-captioning-base"
        )

        if ImageCaptioner._processor is None:

            print(f"Loading BLIP ({model_name})...")

            ImageCaptioner._processor = (
                BlipProcessor.from_pretrained(model_name)
            )

            ImageCaptioner._model = (
                BlipForConditionalGeneration
                .from_pretrained(model_name)
            )

    def _caption_blip(self, image_path):

        image = Image.open(image_path).convert("RGB")

        inputs = ImageCaptioner._processor(
            image,
            return_tensors="pt"
        )

        output = ImageCaptioner._model.generate(
            **inputs,
            max_new_tokens=40
        )

        return ImageCaptioner._processor.decode(
            output[0],
            skip_special_tokens=True
        )

    # ------------------------------------------------------------------

    def caption_image(self, image_path):

        try:

            if self.provider == "gemini":

                return self._caption_gemini(image_path)

            return self._caption_blip(image_path)

        except Exception as e:  # noqa: BLE001

            print(f"Caption error: {e}")

            return ""
