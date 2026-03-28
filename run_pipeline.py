import logging
from pathlib import Path

from config import BATCH_SIZE, LOG_FILE
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
    print("PIPELINE START")
    print("STEP 1: GENERATE")

    prompts = generate_daily_prompts()
    logger.info("Generated %s prompts", len(prompts))
    print("STEP 2: PROCESS")
    batches = _chunk_prompts(prompts, BATCH_SIZE)
    logger.info("Prepared %s batches with batch size %s", len(batches), BATCH_SIZE)
    print("STEP 3: UPLOAD")

    for batch_index, batch in enumerate(batches, start=1):
        logger.info("Processing batch %s/%s with %s prompts", batch_index, len(batches), len(batch))
        failed_prompts = run_workers(batch)
        if failed_prompts:
            logger.error("Batch %s completed with %s unrecovered failures", batch_index, len(failed_prompts))
        logger.info("Batch %s completed", batch_index)

    logger.info("Pipeline finished")
