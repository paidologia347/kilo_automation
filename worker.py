import logging

from queue import task_queue
from utils.browser import generate
from utils.image_processor import process


logger = logging.getLogger(__name__)
MAX_RETRIES = 2


def process_prompt(prompt):
    """Generate an image for *prompt* then run the full post-processing pipeline.

    The browser generation step and the image-processing pipeline are each
    wrapped in their own retry loop so that a transient failure in either
    stage does not silently swallow the error.

    Returns ``True`` when both stages complete successfully, ``False`` when
    all retry attempts are exhausted.
    """
    max_attempts = MAX_RETRIES + 1

    for attempt in range(1, max_attempts + 1):
        try:
            # --- Stage 1: render the prompt to an image -------------------
            generation = generate(prompt)
            image_path = generation["image_path"]
            logger.info(
                "Image rendered in %.2fs (attempt %s/%s): %s",
                generation["render_time"],
                attempt,
                max_attempts,
                image_path,
            )

            # --- Stage 2: upscale → metadata → upload ---------------------
            result = process(image_path=image_path, prompt=prompt)

            if result["success"]:
                logger.info(
                    "Pipeline complete in %.2fs for prompt: %s",
                    result["total_time"],
                    prompt,
                )
                return True

            # A pipeline stage failed — log which one and retry.
            logger.warning(
                "Pipeline stage '%s' failed for prompt '%s' (attempt %s/%s): %s",
                result["failed_stage"],
                prompt,
                attempt,
                max_attempts,
                result["error"],
            )
            if attempt == max_attempts:
                logger.error(
                    "Task permanently failed at stage '%s' for prompt '%s': %s",
                    result["failed_stage"],
                    prompt,
                    result["error"],
                )
                return False

        except Exception as error:
            if attempt < max_attempts:
                logger.warning(
                    "Task failed for prompt '%s' (attempt %s/%s): %s",
                    prompt,
                    attempt,
                    max_attempts,
                    error,
                )
            else:
                logger.error(
                    "Task permanently failed for prompt '%s': %s", prompt, error
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
