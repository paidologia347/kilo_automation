import logging
import time
import traceback
from pathlib import Path

from config import LOG_FILE, SCHEDULE_INTERVAL_SECONDS
from run_pipeline import run_pipeline


def _setup_logging() -> None:
    Path(LOG_FILE).touch(exist_ok=True)
    if not logging.getLogger().handlers:
        logging.basicConfig(
            filename=str(LOG_FILE),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )


def main() -> None:
    _setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("OpenClaw autonomous system starting")
    print("[main] OpenClaw autonomous system starting")

    run_number = 0
    while True:
        run_number += 1
        logger.info("--- Autonomous run #%s begin ---", run_number)
        print(f"[main] Starting autonomous run #{run_number}")
        try:
            run_pipeline()
            logger.info("--- Autonomous run #%s completed successfully ---", run_number)
            print(f"[main] Run #{run_number} completed successfully")
        except Exception:
            tb = traceback.format_exc()
            logger.error(
                "--- Autonomous run #%s failed ---\n%s", run_number, tb
            )
            print(f"[main] Run #{run_number} failed — see {LOG_FILE} for details")

        logger.info(
            "Sleeping %s seconds before next run", SCHEDULE_INTERVAL_SECONDS
        )
        print(
            f"[main] Sleeping {SCHEDULE_INTERVAL_SECONDS}s "
            f"({SCHEDULE_INTERVAL_SECONDS // 3600}h) before next run"
        )
        time.sleep(SCHEDULE_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()

