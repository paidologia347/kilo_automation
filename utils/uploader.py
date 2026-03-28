import logging
import os
from datetime import datetime
from ftplib import FTP, error_perm


logger = logging.getLogger(__name__)
MAX_RETRIES = 2


def upload_file(path: str) -> bool:
    host = os.getenv("FTP_HOST")
    username = os.getenv("FTP_USER")
    password = os.getenv("FTP_PASS")
    folder_name = datetime.now().strftime("%Y-%m-%d")
    max_attempts = MAX_RETRIES + 1

    if not host or not username or not password:
        logger.error("FTP upload skipped: missing FTP_HOST/FTP_USER/FTP_PASS")
        print("[uploader] FTP upload skipped: missing FTP_HOST/FTP_USER/FTP_PASS")
        return False

    for attempt in range(1, max_attempts + 1):
        ftp = None
        try:
            logger.info("FTP upload attempt %s/%s for %s", attempt, max_attempts, path)
            print(f"[uploader] FTP upload attempt {attempt}/{max_attempts} for {path}")
            logger.info("Connecting to FTP host")
            print("[uploader] Connecting to FTP host")
            ftp = FTP(host, timeout=30)
            logger.info("Logging in to FTP server")
            print("[uploader] Logging in to FTP server")
            ftp.login(user=username, passwd=password)
            logger.info("Ensuring remote folder exists: %s", folder_name)
            print(f"[uploader] Ensuring remote folder exists: {folder_name}")
            try:
                ftp.mkd(folder_name)
                logger.info("Created remote folder: %s", folder_name)
                print(f"[uploader] Created remote folder: {folder_name}")
            except error_perm as folder_error:
                message = str(folder_error).lower()
                folder_exists_error = message.startswith("550") and (
                    "exist" in message or "already" in message
                )
                if not folder_exists_error:
                    raise
                logger.info("Remote folder already exists: %s", folder_name)
                print(f"[uploader] Remote folder already exists: {folder_name}")
            logger.info("Changing working directory to %s", folder_name)
            print(f"[uploader] Changing working directory to {folder_name}")
            ftp.cwd(folder_name)
            filename = os.path.basename(path)
            logger.info("Uploading file in binary mode: %s", filename)
            print(f"[uploader] Uploading file in binary mode: {filename}")
            with open(path, "rb") as stream:
                ftp.storbinary(f"STOR {filename}", stream)
            logger.info(
                "Uploaded file to FTP (%s/%s): %s",
                folder_name,
                os.path.basename(path),
                path,
            )
            print(f"[uploader] Uploaded file to FTP ({folder_name}/{filename}): {path}")
            logger.info("Closing FTP connection")
            print("[uploader] Closing FTP connection")
            try:
                ftp.quit()
            except Exception as close_error:
                logger.warning("FTP quit failed: %s", close_error)
                print(f"[uploader] FTP quit failed: {close_error}")
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
                print(
                    "[uploader] FTP upload permanently failed for "
                    f"{path} after {max_attempts} attempts: {error}"
                )
                return False
        finally:
            if ftp is not None:
                try:
                    ftp.close()
                except Exception:
                    pass

    return False


def upload(file_path):
    return upload_file(file_path)
