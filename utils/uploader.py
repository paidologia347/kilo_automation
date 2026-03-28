import logging
import os
from datetime import datetime, timezone
from ftplib import FTP, error_perm


logger = logging.getLogger(__name__)
MAX_RETRIES = 2


def upload_file(path: str) -> bool:
    host = os.getenv("FTP_HOST")
    username = os.getenv("FTP_USER")
    password = os.getenv("FTP_PASS")
    folder_name = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    max_attempts = MAX_RETRIES + 1

    if not host or not username or not password:
        logger.error("FTP upload skipped: missing FTP_HOST/FTP_USER/FTP_PASS")
        return False

    for attempt in range(1, max_attempts + 1):
        try:
            with FTP(host, timeout=30) as ftp:
                ftp.login(user=username, passwd=password)
                try:
                    ftp.mkd(folder_name)
                except error_perm:
                    # Folder may already exist on the remote server.
                    pass
                ftp.cwd(folder_name)
                with open(path, "rb") as stream:
                    ftp.storbinary(f"STOR {os.path.basename(path)}", stream)

            logger.info(
                "Uploaded file to FTP (%s/%s): %s",
                folder_name,
                os.path.basename(path),
                path,
            )
            return True
        except Exception as error:
            if attempt < max_attempts:
                logger.warning(
                    "FTP upload failed for %s (attempt %s/%s): %s",
                    path,
                    attempt,
                    max_attempts,
                    error,
                )
            else:
                logger.error(
                    "FTP upload permanently failed for %s after %s attempts: %s",
                    path,
                    max_attempts,
                    error,
                )
                return False

    return False


def upload(file_path):
    return upload_file(file_path)
