from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/bitbucket-webhook', methods=['POST'])
def handle_webhook():
    data = request.json  # Parse the webhook payload
    
    # Extract the necessary info, e.g., commit hash or modified files
    commits = data.get("push", {}).get("changes", [])
    
    for commit in commits:
        # Example: Process each file in the commit
        for file in commit.get("files", []):
            file_path = file['path']
            
            # Fetch the file from Bitbucket API
            response = requests.get(
                f"https://api.bitbucket.org/2.0/repositories/<user>/<repo>/src/{file_path}",
                headers={"Authorization": "Bearer <your-access-token>"}
            )
            
            # Transfer the file to the desired location (e.g., S3, FTP)
            transfer_file(response.content, destination="s3://your-bucket/your-path")

    return jsonify({"status": "success"}), 200

def transfer_file(content, destination):
    # Example function to upload file content to S3 or other location
    # Here you would implement the transfer logic
    pass

if __name__ == '__main__':
    app.run(port=5000)
