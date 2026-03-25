import logging

from queue import task_queue
from utils.browser import generate
from utils.metadata import meta
from utils.upscale import upscale
from utils.uploader import upload


logger = logging.getLogger(__name__)
MAX_RETRIES = 2


def process_prompt(prompt):
    max_attempts = MAX_RETRIES + 1
    for attempt in range(1, max_attempts + 1):
        try:
            output_file = generate(prompt)
            upscaled_file = upscale(output_file)
            meta(upscaled_file, prompt)
            upload(upscaled_file)
            logger.info("Task succeeded for prompt: %s", prompt)
            return True
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
                logger.error("Task permanently failed for prompt '%s': %s", prompt, error)
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
