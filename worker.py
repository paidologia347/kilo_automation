import logging
import random
import time
from typing import Optional

from config import DELAY_MAX, DELAY_MIN, RETRY
from queue import task_queue
from utils.browser import generate_image
from utils.metadata import inject_metadata
from utils.upscale import upscale_image
from utils.uploader import upload_file


logger = logging.getLogger(__name__)


def _get_delay_bounds() -> tuple[float, float]:
    if DELAY_MIN > DELAY_MAX:
        logger.warning(
            "DELAY_MIN (%s) is greater than DELAY_MAX (%s); swapping values",
            DELAY_MIN,
            DELAY_MAX,
        )
        return DELAY_MAX, DELAY_MIN
    return DELAY_MIN, DELAY_MAX


def process_prompt(prompt: str) -> bool:
    """Generate, upscale, inject metadata, then upload for a single prompt."""
    try:
        logger.info("Prompt start: %s", prompt)
        logger.info("Step 1/4: generating image")
        image_path = generate_image(prompt)
        logger.info("Step 1/4 complete: image generated at %s", image_path)
        logger.info("Step 2/4: upscaling image")
        upscaled_path = upscale_image(image_path)
        logger.info("Step 2/4 complete: upscaled image at %s", upscaled_path)
        logger.info("Step 3/4: injecting metadata")
        final_path = inject_metadata(upscaled_path, prompt)
        logger.info("Step 3/4 complete: metadata injected into %s", final_path)
        logger.info("Step 4/4: uploading file")
        uploaded = upload_file(final_path)
        if not uploaded:
            logger.error("Step 4/4 failed uploading %s", final_path)
            logger.error("Prompt failed: %s", prompt)
            return False

        logger.info("Step 4/4 complete: uploaded %s", final_path)
        logger.info("Prompt succeeded: %s", prompt)
        return True
    except Exception as error:
        logger.exception("Prompt failed: %s (%s)", prompt, error)
        return False


def process_prompts(prompts: list[str]) -> list[str]:
    """Run the full pipeline for each prompt and return failed prompts."""
    failed_prompts = []
    delay_min, delay_max = _get_delay_bounds()

    for index, prompt in enumerate(prompts, start=1):
        logger.info("Processing prompt %s/%s", index, len(prompts))
        attempt = 0
        succeeded = False
        max_attempts = RETRY + 1

        while attempt < max_attempts and not succeeded:
            attempt += 1
            logger.info(
                "Prompt attempt %s/%s for prompt %s/%s",
                attempt,
                max_attempts,
                index,
                len(prompts),
            )
            succeeded = process_prompt(prompt)
            if not succeeded and attempt < max_attempts:
                logger.warning(
                    "Prompt attempt %s failed for prompt %s/%s; retrying",
                    attempt,
                    index,
                    len(prompts),
                )
                retry_delay = random.uniform(delay_min, delay_max)
                logger.info("Sleeping %.2f seconds before retry", retry_delay)
                time.sleep(retry_delay)
        if not succeeded:
            failed_prompts.append(prompt)

        if index < len(prompts):
            delay_seconds = random.uniform(delay_min, delay_max)
            logger.info("Sleeping %.2f seconds before next prompt", delay_seconds)
            time.sleep(delay_seconds)

    return failed_prompts


def run_workers(prompts: Optional[list[str]] = None) -> list[str]:
    if prompts is not None:
        return process_prompts(prompts)

    queued_prompts = []
    while not task_queue.empty():
        prompt = None
        try:
            prompt = task_queue.get()
            queued_prompts.append(prompt)
        except Exception as error:
            logger.exception("Worker failed reading queued prompt '%s': %s", prompt, error)
        finally:
            if prompt is not None:
                task_queue.task_done()

    return process_prompts(queued_prompts)
