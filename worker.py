import logging

from queue import task_queue
from utils.browser import generate
from utils.metadata import meta
from utils.upscale import upscale
from utils.uploader import upload


logger = logging.getLogger(__name__)
MAX_RETRIES = 2


def process_prompt(prompt):
    attempt = 0
    while attempt <= MAX_RETRIES:
        try:
            output_file = generate(prompt)
            upscaled_file = upscale(output_file)
            meta(upscaled_file, prompt)
            upload(upscaled_file)
            logger.info("Task succeeded for prompt: %s", prompt)
            return True
        except Exception as error:
            attempt += 1
            if attempt <= MAX_RETRIES:
                logger.warning(
                    "Task failed for prompt '%s' (attempt %s/%s): %s",
                    prompt,
                    attempt,
                    MAX_RETRIES,
                    error,
                )
            else:
                logger.error("Task permanently failed for prompt '%s': %s", prompt, error)
                return False


def run_workers():
    while not task_queue.empty():
        prompt = task_queue.get()
        process_prompt(prompt)
        task_queue.task_done()
