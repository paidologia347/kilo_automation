import logging
from pathlib import Path

from PIL import Image


logger = logging.getLogger(__name__)


def upscale_image(path: str) -> str:
    try:
        source = Path(path)
        with Image.open(source) as image:
            resampling = getattr(Image, "Resampling", Image)
            upscaled = image.resize(
                (image.width * 2, image.height * 2),
                resampling.LANCZOS,
            )
            output_path = source.with_name(f"{source.stem}_2x{source.suffix}")
            upscaled.save(output_path)

        logger.info("Upscaled image saved: %s", output_path)
        return str(output_path)
    except Exception as error:
        logger.exception("Failed to upscale image %s: %s", path, error)
        raise


def upscale(file_path):
    return upscale_image(file_path)
