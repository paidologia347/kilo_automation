import logging
import os
from datetime import datetime, timezone
from ftplib import FTP, error_perm
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)
MAX_RETRIES = 2
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def _dual_log(level: int, message: str, *args: object) -> None:
    logger.log(level, message, *args)
    try:
        formatted = message % args if args else message
    except (TypeError, ValueError):
        formatted = message
    print(f"[uploader] {formatted}")


def _validate_file_path(path: str) -> Optional[Path]:
    if not path:
        _dual_log(logging.ERROR, "FTP upload skipped: empty file path")
        return None
    file_path = Path(path)
    if not file_path.exists():
        _dual_log(logging.ERROR, "FTP upload skipped: file not found: %s", path)
        return None
    if not file_path.is_file():
        _dual_log(logging.ERROR, "FTP upload skipped: not a file: %s", path)
        return None
    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        _dual_log(
            logging.ERROR,
            "FTP upload skipped: unsupported file extension %s for %s",
            file_path.suffix,
            path,
        )
        return None
    return file_path


def upload_file(path: str, max_retries: int = MAX_RETRIES) -> bool:
    if max_retries < 0:
        _dual_log(
            logging.WARNING,
            "FTP upload retry count was negative (%s); clamping to 0",
            max_retries,
        )
        max_retries = 0
    host = os.getenv("FTP_HOST")
    username = os.getenv("FTP_USER")
    password = os.getenv("FTP_PASS")
    folder_name = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    max_attempts = max_retries + 1
    file_path = _validate_file_path(path)
    if file_path is None:
        return False

    if not host or not username or not password:
        _dual_log(
            logging.ERROR,
            "FTP upload skipped: missing FTP_HOST/FTP_USER/FTP_PASS",
        )
        return False
    for attempt in range(1, max_attempts + 1):
        try:
            _dual_log(
                logging.INFO,
                "FTP upload attempt %s/%s for %s",
                attempt,
                max_attempts,
                path,
            )
            print("CONNECTING FTP")
            _dual_log(logging.INFO, "Connecting to FTP host: %s", host)
            with FTP(host, timeout=30) as ftp:
                _dual_log(logging.INFO, "Logging in to FTP server")
                ftp.login(user=username, passwd=password)
                _dual_log(logging.INFO, "Ensuring remote folder exists: %s", folder_name)
                try:
                    ftp.mkd(folder_name)
                    _dual_log(logging.INFO, "Created remote folder: %s", folder_name)
                except error_perm as folder_error:
                    message = str(folder_error).lower()
                    folder_exists_error = message.startswith("550") and (
                        "exist" in message or "already" in message
                    )
                    if not folder_exists_error:
                        raise
                    _dual_log(logging.INFO, "Remote folder already exists: %s", folder_name)
                _dual_log(logging.INFO, "Changing working directory to %s", folder_name)
                ftp.cwd(folder_name)
                filename = file_path.name
                print("UPLOADING FILE")
                _dual_log(logging.INFO, "Uploading file in binary mode: %s", filename)
                with file_path.open("rb") as stream:
                    ftp.storbinary(f"STOR {filename}", stream)
                print("UPLOAD SUCCESS")
                _dual_log(
                    logging.INFO,
                    "Uploaded file to FTP (%s/%s): %s",
                    folder_name,
                    filename,
                    str(file_path),
                )
            _dual_log(logging.INFO, "FTP connection closed successfully")
            return True
        except Exception as error:
            if attempt < max_attempts:
                _dual_log(
                    logging.WARNING,
                    "FTP upload failed for %s (attempt %s/%s): %s",
                    path,
                    attempt,
                    max_attempts,
                    error,
                )
            else:
                _dual_log(
                    logging.ERROR,
                    "FTP upload permanently failed for %s after %s attempts: %s",
                    path,
                    max_attempts,
                    error,
                )
                return False

    return False


def upload(file_path):
    return upload_file(file_path)
