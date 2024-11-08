from flask import Flask, jsonify, make_response, request
from flask_cors import CORS, cross_origin
import requests
import subprocess
import time

app = Flask(__name__)
cors = CORS(app)

gold_endpoint_status = {}

def check_service(url):
    try:
        payload = {"gold_type": "vang24k"}
        response = requests.post(url, json=payload, timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def endpoint_health_check():
    endpoint_status = {
        "gold_price_api_online": check_service("http://localhost:3007/"),
    }
    # Return a regular dictionary instead of using jsonify
    return {"services": endpoint_status}

import subprocess
import json

def get_container_stats(container_name):
    # Get general status info using `docker inspect`
    inspect_cmd = f"docker inspect {container_name}"
    try:
        inspect_result = subprocess.run(inspect_cmd, shell=True, capture_output=True, text=True, check=True)
        inspect_data = json.loads(inspect_result.stdout)[0]  # Parse JSON output

        # Extract necessary info from `docker inspect`
        status = inspect_data["State"]["Status"]
        running = inspect_data["State"]["Running"]
        pid = inspect_data["State"]["Pid"]
        created = inspect_data["Created"]
        memory_limit = inspect_data["HostConfig"]["Memory"]

    except subprocess.CalledProcessError as e:
        print(f"Failed to inspect container: {e}")
        return {"error": "Failed to retrieve container inspect data"}

    # Get live stats using `docker stats` in no-stream mode
    stats_cmd = f"docker stats {container_name} --no-stream --format " \
                "'{{json .}}'"  # Get stats as JSON formatted output
    try:
        stats_result = subprocess.run(stats_cmd, shell=True, capture_output=True, text=True, check=True)
        stats_data = json.loads(stats_result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Failed to get container stats: {e}")
        stats_data = {"error": "Failed to retrieve container live stats"}

    # Combine `inspect` and `stats` data into one JSON-like dictionary
    container_info = {
        "status": status,
        "running": running,
        "pid": pid,
        "created": created,
        "memory_limit": memory_limit,
        "live_stats": stats_data
    }
    return container_info  # Return as JSON-ready dictionary

@app.route('/', methods=['GET'])
@cross_origin()
def health_check():
    container_name = "b6d31cf7c8bebb688ea91f2293fc4b1e43c7286e8cb1a08b9ee6c18efc21d5aa"
    global gold_endpoint_status
    report = endpoint_health_check()
    if report:
            gold_endpoint_status = report 
            print("Updated gold_endpoint_status:", gold_endpoint_status)
    else:
         print("Warning: Received empty or invalid report")

    try:
         container_status = get_container_stats(container_name)
    except Exception as e:
         print(f"Failed to get container status")
    
    gold_service_status = {
        "gold_endpoint_status": gold_endpoint_status,
        "container_status": container_status
    }
    return jsonify(gold_service_status)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4007)

