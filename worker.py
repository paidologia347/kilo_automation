import logging

from queue import task_queue
from utils.browser import generate as generate_image
from utils.metadata import inject_metadata
from utils.upscale import upscale_image


logger = logging.getLogger(__name__)
MAX_RETRIES = 2


def process_prompt(prompt):
    """Generate an image then run upscale and metadata steps with retries."""
    max_attempts = MAX_RETRIES + 1

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info("Step 1/3: generating image (attempt %s/%s)", attempt, max_attempts)
            generation = generate_image(prompt)
            image_path = generation["image_path"]
            logger.info("Step 1/3 complete: image generated at %s", image_path)
            logger.info("Step 2/3: upscaling image")
            upscaled_path = upscale_image(image_path)
            logger.info("Step 2/3 complete: upscaled image at %s", upscaled_path)
            logger.info("Step 3/3: injecting metadata")
            final_path = inject_metadata(upscaled_path, prompt)
            logger.info("Step 3/3 complete: metadata injected into %s", final_path)
            logger.info("Pipeline complete for prompt: %s", prompt)
            return True

        except Exception as error:
            if attempt < max_attempts:
                logger.warning(
                    "Pipeline failed for prompt '%s' (attempt %s/%s): %s",
                    prompt,
                    attempt,
                    max_attempts,
                    error,
                )
            else:
                logger.error(
                    "Pipeline permanently failed for prompt '%s': %s", prompt, error
                )
                return False

    return False


def run_workers():
    while not task_queue.empty():
        prompt = None
        try:
            prompt = task_queue.get()
            process_prompt(prompt)
        except Exception as error:
            logger.exception("Worker failed processing prompt '%s': %s", prompt, error)
        finally:
            if prompt is not None:
                task_queue.task_done()
