from flask import Flask, request, jsonify
import logging
from prometheus_client import start_http_server, Counter
from datetime import datetime

app = Flask(__name__)

log_filename = datetime.now().strftime("webhook_%Y%m%d_%H%M%S.log")
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

RECEIVED_FILES = Counter('webhook_received_files', 'Count of files received by webhook')
FAILED_RECEIPTS = Counter('webhook_failed_receipts', 'Count of failed file receptions')

@app.route("/webhook", methods=["POST"])
def receive_file():
    try:
        if 'file' not in request.files:
            logging.warning("No file part in the request")
            FAILED_RECEIPTS.inc()
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        file_name = file.filename
        file.save(f"/app/{file_name}")
        logging.info(f"Received and saved file: {file_name}")
        RECEIVED_FILES.inc()
        return jsonify({"status": "success", "file_name": file_name})
    except Exception as e:
        logging.error(f"Failed to process file upload: {e}")
        FAILED_RECEIPTS.inc()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    start_http_server(8002)
    app.run(host="0.0.0.0", port=5000)

