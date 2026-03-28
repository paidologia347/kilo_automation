"""Automatic post-processing pipeline for generated images.

Pipeline stages
---------------
1. **Upscale** – doubles the image resolution via ``utils.upscale.upscale``.
2. **Metadata** – embeds EXIF metadata (prompt, description) via
   ``utils.metadata.meta``.
3. **Upload** – transfers the finished file via ``utils.uploader.upload``.

Usage::

    from utils.image_processor import process

    result = process(image_path="/outputs/output_123.jpg", prompt="a sunset")
    # result["success"] is True when all stages complete without error.
"""

import logging
import time

from utils.upscale import upscale
from utils.metadata import meta
from utils.uploader import upload


logger = logging.getLogger(__name__)


def process(image_path: str, prompt: str) -> dict:
    """Run the full post-processing pipeline on *image_path*.

    Each stage is attempted in order.  If a stage raises an exception the
    pipeline is aborted immediately and the returned dict reflects the failure
    so the caller can decide how to handle it (e.g. retry the whole task).

    Parameters
    ----------
    image_path:
        Path to the raw image produced by ``utils.browser.generate``.
    prompt:
        The original text prompt; forwarded to the metadata stage.

    Returns
    -------
    dict with the following keys:

    ``success`` (bool)
        ``True`` when every stage completed without error.
    ``image_path`` (str)
        Path to the *original* image that was passed in.
    ``upscaled_path`` (str | None)
        Path to the upscaled image, or ``None`` if upscaling failed.
    ``metadata_path`` (str | None)
        Path returned by the metadata stage (same file, in-place), or
        ``None`` if that stage was not reached / failed.
    ``uploaded`` (bool)
        ``True`` when the upload stage completed successfully.
    ``total_time`` (float)
        Wall-clock seconds for the entire pipeline.
    ``error`` (str | None)
        Human-readable error message for the first stage that failed, or
        ``None`` on full success.
    ``failed_stage`` (str | None)
        Name of the stage that raised (``"upscale"``, ``"metadata"``, or
        ``"upload"``), or ``None`` on full success.
    """
    result: dict = {
        "success": False,
        "image_path": image_path,
        "upscaled_path": None,
        "metadata_path": None,
        "uploaded": False,
        "total_time": 0.0,
        "error": None,
        "failed_stage": None,
    }

    pipeline_start = time.monotonic()

    # ------------------------------------------------------------------
    # Stage 1 – Upscale
    # ------------------------------------------------------------------
    logger.info("[image_processor] upscaling %s", image_path)
    try:
        upscaled_path = upscale(image_path)
        result["upscaled_path"] = upscaled_path
        logger.info("[image_processor] upscale complete: %s", upscaled_path)
    except Exception as exc:
        result["failed_stage"] = "upscale"
        result["error"] = str(exc)
        result["total_time"] = time.monotonic() - pipeline_start
        logger.error(
            "[image_processor] upscale failed for %s: %s", image_path, exc
        )
        return result

    # ------------------------------------------------------------------
    # Stage 2 – Metadata injection
    # ------------------------------------------------------------------
    logger.info("[image_processor] injecting metadata into %s", upscaled_path)
    try:
        metadata_path = meta(upscaled_path, prompt)
        result["metadata_path"] = metadata_path
        logger.info("[image_processor] metadata injected: %s", metadata_path)
    except Exception as exc:
        result["failed_stage"] = "metadata"
        result["error"] = str(exc)
        result["total_time"] = time.monotonic() - pipeline_start
        logger.error(
            "[image_processor] metadata injection failed for %s: %s",
            upscaled_path,
            exc,
        )
        return result

    # ------------------------------------------------------------------
    # Stage 3 – Upload
    # ------------------------------------------------------------------
    logger.info("[image_processor] uploading %s", upscaled_path)
    try:
        upload(upscaled_path)
        result["uploaded"] = True
        logger.info("[image_processor] upload complete: %s", upscaled_path)
    except Exception as exc:
        result["failed_stage"] = "upload"
        result["error"] = str(exc)
        result["total_time"] = time.monotonic() - pipeline_start
        logger.error(
            "[image_processor] upload failed for %s: %s", upscaled_path, exc
        )
        return result

    # ------------------------------------------------------------------
    # All stages succeeded
    # ------------------------------------------------------------------
    result["success"] = True
    result["total_time"] = time.monotonic() - pipeline_start
    logger.info(
        "[image_processor] pipeline complete in %.2fs for prompt %r",
        result["total_time"],
        prompt,
    )
    return result
