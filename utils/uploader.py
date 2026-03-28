import logging
import os
from datetime import datetime, timezone
from ftplib import FTP, error_perm


logger = logging.getLogger(__name__)
MAX_RETRIES = 2


def _log_with_print(level: int, message: str, *args: object) -> None:
    logger.log(level, message, *args)
    try:
        formatted = message % args if args else message
    except TypeError:
        formatted = message
    print(f"[uploader] {formatted}")


def upload_file(path: str) -> bool:
    host = os.getenv("FTP_HOST")
    username = os.getenv("FTP_USER")
    password = os.getenv("FTP_PASS")
    folder_name = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    max_attempts = MAX_RETRIES + 1

    if not host or not username or not password:
        _log_with_print(
            logging.ERROR,
            "FTP upload skipped: missing FTP_HOST/FTP_USER/FTP_PASS",
        )
        return False

    for attempt in range(1, max_attempts + 1):
        ftp = None
        try:
            _log_with_print(
                logging.INFO,
                "FTP upload attempt %s/%s for %s",
                attempt,
                max_attempts,
                path,
            )
            _log_with_print(logging.INFO, "Connecting to FTP host")
            ftp = FTP(host, timeout=30)
            _log_with_print(logging.INFO, "Logging in to FTP server")
            ftp.login(user=username, passwd=password)
            _log_with_print(logging.INFO, "Ensuring remote folder exists: %s", folder_name)
            try:
                ftp.mkd(folder_name)
                _log_with_print(logging.INFO, "Created remote folder: %s", folder_name)
            except error_perm as folder_error:
                message = str(folder_error).lower()
                folder_exists_error = message.startswith("550") and (
                    "exist" in message or "already" in message
                )
                if not folder_exists_error:
                    raise
                _log_with_print(logging.INFO, "Remote folder already exists: %s", folder_name)
            _log_with_print(logging.INFO, "Changing working directory to %s", folder_name)
            ftp.cwd(folder_name)
            filename = os.path.basename(path)
            _log_with_print(logging.INFO, "Uploading file in binary mode: %s", filename)
            with open(path, "rb") as stream:
                ftp.storbinary(f"STOR {filename}", stream)
            _log_with_print(
                logging.INFO,
                "Uploaded file to FTP (%s/%s): %s",
                folder_name,
                filename,
                path,
            )
            return True
        except Exception as error:
            if attempt < max_attempts:
                _log_with_print(
                    logging.WARNING,
                    "FTP upload failed for %s (attempt %s/%s): %s",
                    path,
                    attempt,
                    max_attempts,
                    error,
                )
            else:
                _log_with_print(
                    logging.ERROR,
                    "FTP upload permanently failed for %s after %s attempts: %s",
                    path,
                    max_attempts,
                    error,
                )
                return False
        finally:
            if ftp is not None:
                try:
                    _log_with_print(logging.INFO, "Closing FTP connection")
                    ftp.quit()
                except Exception:
                    try:
                        ftp.close()
                    except Exception:
                        pass

    return False


def upload(file_path):
    return upload_file(file_path)
