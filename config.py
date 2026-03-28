import os
from pathlib import Path


BATCH_SIZE = int(os.getenv("BATCH_SIZE", "20"))
DELAY_MIN = float(os.getenv("DELAY_MIN", "5"))
DELAY_MAX = float(os.getenv("DELAY_MAX", "10"))
RETRY = int(os.getenv("RETRY", "2"))
UPLOAD_DELAY_SECONDS = float(os.getenv("UPLOAD_DELAY_SECONDS", "5"))
UPLOAD_RETRY_ATTEMPTS = int(os.getenv("UPLOAD_RETRY_ATTEMPTS", "2"))
PROMPT_COUNT_MIN = int(os.getenv("PROMPT_COUNT_MIN", "100"))
PROMPT_COUNT_MAX = int(os.getenv("PROMPT_COUNT_MAX", "150"))
SCHEDULE_INTERVAL_SECONDS = int(os.getenv("SCHEDULE_INTERVAL_SECONDS", str(24 * 60 * 60)))
LOG_FILE = Path("log.txt")
