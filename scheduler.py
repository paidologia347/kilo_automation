import logging
import time

from config import SCHEDULE_INTERVAL_SECONDS
from run_pipeline import run_pipeline

logger = logging.getLogger(__name__)


def run_scheduler() -> None:
    while True:
        try:
            logger.info("Scheduler tick: starting pipeline run")
            run_pipeline()
        except Exception as error:
            logger.exception("Scheduler pipeline run failed: %s", error)
        logger.info("Scheduler sleeping for %s seconds", SCHEDULE_INTERVAL_SECONDS)
        time.sleep(SCHEDULE_INTERVAL_SECONDS)
