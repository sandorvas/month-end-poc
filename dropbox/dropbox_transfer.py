import dropbox
import os
import logging
from prometheus_client import start_http_server, Counter
from datetime import datetime

# Set up logging with timestamped filename
log_filename = datetime.now().strftime("dropbox_transfer_%Y%m%d_%H%M%S.log")
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Prometheus metrics
UPLOAD_SUCCESS = Counter('dropbox_upload_success', 'Count of successful Dropbox uploads')
UPLOAD_FAILURE = Counter('dropbox_upload_failure', 'Count of failed Dropbox uploads')

DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
assert DROPBOX_ACCESS_TOKEN, "Dropbox access token not provided"
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

def upload_file(file_path, dropbox_path):
    try:
        with open(file_path, "rb") as file:
            dbx.files_upload(file.read(), dropbox_path)
            logging.info(f"Uploaded {file_path} to Dropbox at {dropbox_path}.")
            UPLOAD_SUCCESS.inc()
    except Exception as e:
        logging.error(f"Failed to upload {file_path} to Dropbox: {e}")
        UPLOAD_FAILURE.inc()
        raise

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8001)
    upload_file("example_file.txt", "/example_upload.txt")

