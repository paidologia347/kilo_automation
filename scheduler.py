import logging
import time

from config import SCHEDULE_INTERVAL_SECONDS
from run_pipeline import run_pipeline


def run_scheduler() -> None:
    logger = logging.getLogger(__name__)
    while True:
        logger.info("Scheduler tick: starting pipeline run")
        run_pipeline()
        logger.info("Scheduler sleeping for %s seconds", SCHEDULE_INTERVAL_SECONDS)
        time.sleep(SCHEDULE_INTERVAL_SECONDS)
