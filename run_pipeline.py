import logging
from pathlib import Path

from config import BATCH_SIZE, LOG_FILE, RETRY
from prompt_engine import generate_daily_prompts
from worker import run_workers


def _setup_logging() -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(
            filename=str(LOG_FILE),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )
    Path(LOG_FILE).touch(exist_ok=True)


def _chunk_prompts(prompts: list[str], batch_size: int) -> list[list[str]]:
    return [prompts[idx : idx + batch_size] for idx in range(0, len(prompts), batch_size)]


def run_pipeline() -> None:
    _setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Pipeline started")

    prompts = generate_daily_prompts()
    logger.info("Generated %s prompts", len(prompts))
    batches = _chunk_prompts(prompts, BATCH_SIZE)
    logger.info("Prepared %s batches with batch size %s", len(batches), BATCH_SIZE)

    for batch_index, batch in enumerate(batches, start=1):
        logger.info("Processing batch %s/%s with %s prompts", batch_index, len(batches), len(batch))
        failed_prompts = run_workers(batch)

        attempt = 1
        while failed_prompts and attempt <= RETRY:
            logger.warning(
                "Retrying %s failed prompts in batch %s (retry %s/%s)",
                len(failed_prompts),
                batch_index,
                attempt,
                RETRY,
            )
            failed_prompts = run_workers(failed_prompts)
            attempt += 1

        if failed_prompts:
            logger.error(
                "Batch %s completed with %s unrecovered failures",
                batch_index,
                len(failed_prompts),
            )
        else:
            logger.info("Batch %s completed successfully", batch_index)

    logger.info("Pipeline finished")
