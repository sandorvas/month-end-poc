import grpc
from concurrent import futures
import file_transfer_pb2
import file_transfer_pb2_grpc
import logging
from prometheus_client import start_http_server, Counter
from datetime import datetime

log_filename = datetime.now().strftime("grpc_server_%Y%m%d_%H%M%S.log")
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

RECEIVED_FILES = Counter('grpc_received_files', 'Count of files received by gRPC')
FAILED_RECEIPTS = Counter('grpc_failed_receipts', 'Count of failed file receptions')

class FileTransferService(file_transfer_pb2_grpc.FileTransferServicer):
    def SendFile(self, request, context):
        try:
            file_name = request.file_name
            with open(f"/app/{file_name}", "wb") as f:
                f.write(request.file_content)
            RECEIVED_FILES.inc()
            logging.info(f"Received and saved file: {file_name}")
            return file_transfer_pb2.FileResponse(message="File received successfully!")
        except Exception as e:
            FAILED_RECEIPTS.inc()
            logging.error(f"Failed to save file {file_name}: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error: {e}")
            return file_transfer_pb2.FileResponse(message="File saving failed")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_transfer_pb2_grpc.add_FileTransferServicer_to_server(FileTransferService(), server)
    server.add_insecure_port("[::]:50051")
    logging.info("gRPC server starting on port 50051")
    start_http_server(8003)  # Prometheus metrics server
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

