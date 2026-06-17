from PIL import Image

from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration
)


class ImageCaptioner:

    _processor = None

    _model = None

    def __init__(self):

        if ImageCaptioner._processor is None:

            print(
                "Loading BLIP..."
            )

            ImageCaptioner._processor = (
                BlipProcessor.from_pretrained(
                    "Salesforce/blip-image-captioning-base"
                )
            )

            ImageCaptioner._model = (
                BlipForConditionalGeneration
                .from_pretrained(
                    "Salesforce/blip-image-captioning-base"
                )
            )

    def caption_image(
        self,
        image_path
    ):

        try:

            image = Image.open(
                image_path
            ).convert(
                "RGB"
            )

            inputs = (
                self._processor(
                    image,
                    return_tensors="pt"
                )
            )

            output = (
                self._model.generate(
                    **inputs,
                    max_new_tokens=40
                )
            )

            caption = (
                self._processor.decode(
                    output[0],
                    skip_special_tokens=True
                )
            )

            return caption

        except Exception as e:

            print(
                f"BLIP Error: {e}"
            )

            return ""