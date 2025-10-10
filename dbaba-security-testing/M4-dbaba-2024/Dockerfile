# Dockerfile for DBABA Application
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY dbaba/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir flask

# Expose port
EXPOSE 5000

# Create a simple Flask wrapper for the CLI application
RUN echo 'from flask import Flask, request, jsonify\n\
import subprocess\n\
import os\n\
\n\
app = Flask(__name__)\n\
\n\
@app.route("/")\n\
def home():\n\
    return """<h1>DBABA Address Book Application</h1>\n\
    <p>CLI-based address book for security testing</p>\n\
    <ul>\n\
        <li><a href="/status">Status</a></li>\n\
        <li><a href="/version">Version</a></li>\n\
    </ul>"""\n\
\n\
@app.route("/status")\n\
def status():\n\
    return jsonify({"status": "running", "app": "DBABA"})\n\
\n\
@app.route("/version")\n\
def version():\n\
    return jsonify({"version": "0.3", "name": "Address Book Application"})\n\
\n\
@app.route("/execute", methods=["POST"])\n\
def execute():\n\
    """Execute DBABA commands - VULNERABLE endpoint for testing"""\n\
    cmd = request.json.get("command", "")\n\
    # Intentionally vulnerable for security testing\n\
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)\n\
    return jsonify({"output": result.stdout, "error": result.stderr})\n\
\n\
if __name__ == "__main__":\n\
    app.run(host="0.0.0.0", port=5000, debug=True)\n\
' > /app/app.py

CMD ["python", "app.py"]

