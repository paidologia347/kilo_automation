import logging
from pathlib import Path

import piexif


logger = logging.getLogger(__name__)


def meta(file_path, prompt):
    try:
        image_path = Path(file_path)
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        title = f"Generated image for: {prompt}".encode("utf-8")
        description = f"Automation output prompt: {prompt}".encode("utf-8")

        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = description
        exif_dict["0th"][piexif.ImageIFD.XPTitle] = title

        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, str(image_path))

        logger.info("Metadata injected into %s", image_path)
        return str(image_path)
    except Exception as error:
        logger.exception("Failed injecting metadata into %s: %s", file_path, error)
        raise
