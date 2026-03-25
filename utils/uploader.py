import logging
import os
from ftplib import FTP


logger = logging.getLogger(__name__)


def upload(file_path):
    try:
        host = os.getenv("FTP_HOST", "ftp.example.com")
        username = os.getenv("FTP_USERNAME", "your_username")
        password = os.getenv("FTP_PASSWORD", "your_password")

        with FTP(host, timeout=30) as ftp:
            ftp.login(user=username, passwd=password)
            with open(file_path, "rb") as stream:
                ftp.storbinary(f"STOR {os.path.basename(file_path)}", stream)

        logger.info("Uploaded file: %s", file_path)
        return True
    except Exception as error:
        logger.exception("Failed to upload file %s: %s", file_path, error)
        raise
