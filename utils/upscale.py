import logging
from pathlib import Path

from PIL import Image


logger = logging.getLogger(__name__)


def upscale(file_path):
    try:
        source = Path(file_path)
        with Image.open(source) as image:
            upscaled = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)
            output_path = source.with_name(f"{source.stem}_2x{source.suffix}")
            upscaled.save(output_path)

        logger.info("Upscaled image saved: %s", output_path)
        return str(output_path)
    except Exception as error:
        logger.exception("Failed to upscale image %s: %s", file_path, error)
        raise
