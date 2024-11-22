import json
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import requests
import subprocess
import time
import threading
from datetime import datetime, timedelta

app = Flask(__name__)
cors = CORS(app)

monitoringInfos = [
    {
        "container_name": "exchange_rate_service_no1",
        "API": "http://localhost:3004/"
    },
    {
        "container_name": "exchange_rate_service_no2",
        "API": "http://localhost:3005/"
    }
]


def check_service(url):
    try:
        payload = {"currency": "USD"}
        print(f"Response from {url}")
        response = requests.post(url, json=payload, timeout=5)
        print(f"Response status code: {response.status_code}")
        return response.status_code == 200
    except requests.RequestException:
        return False


def endpoint_health_check(api):
    endpoint_status = {
        "online": check_service(api),
    }
    # Return a regular dictionary instead of using jsonify
    return {"services": endpoint_status}


def get_container_stats(container_name):
    # Get general status info using `docker inspect`
    inspect_cmd = f"docker inspect {container_name}"
    try:
        inspect_result = subprocess.run(
            inspect_cmd, shell=True, capture_output=True, text=True, check=True)
        inspect_data = json.loads(inspect_result.stdout)[
            0]  # Parse JSON output

        # Extract necessary info from `docker inspect`
        status = inspect_data["State"]["Status"]
        created_time = inspect_data["Created"].split(".")[0]
        created_time = datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%S")
        created_time = (created_time + timedelta(hours=7)
                        ).strftime("%Y-%m-%dT%H:%M:%S")

    except subprocess.CalledProcessError as e:
        print(f"Failed to inspect container: {e}")
        return {"error": "Failed to retrieve container inspect data"}

    # Get live stats using `docker stats` in no-stream mode
    # Get stats as JSON formatted output

    stats_cmd = ["docker", "stats", container_name,
                 "--no-stream", "--format", "{{json .}}"]

    try:
        stats_result = subprocess.run(
            stats_cmd, capture_output=True, text=True, check=True)
        stats_data = json.loads(stats_result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Failed to get container stats: {e}")
        print(f"stderr: {e.stderr}")
        stats_data = {"error": "Failed to retrieve container live stats"}

    # Combine `inspect` and `stats` data into one JSON-like dictionary
    container_info = {
        "status": status,
        "created": created_time,
        "live_stats": {
            "CPUPerc": stats_data.get("CPUPerc", ""),
            "MemPerc": stats_data.get("MemPerc", ""),
            "MemUsage": stats_data.get("MemUsage"),
            "NetIO": stats_data.get("NetIO")
        }
    }
    return container_info  # Return as JSON-ready dictionary


@app.route('/', methods=['GET'])
@cross_origin()
def health_check():
    exchange_service_status = []
    threads = []

    def process_container(each_container):
        container_name = each_container["container_name"]
        api = each_container["API"]
        report = endpoint_health_check(api)
        if report:
            exchange_endpoint_status = report
            print("Updated exchange_endpoint_status:", exchange_endpoint_status)
        else:
            print("Warning: Received empty or invalid report")

        # Initialize with default value
        container_info = {"error": "Failed to retrieve container stats"}

        try:
            container_info = get_container_stats(container_name)
        except Exception as e:
            print(f"Failed to get container status: {e}")

        exchange_service_status.append({
            "container_name": container_name,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() + 7*3600)),
            "created_at": container_info.get("created"),
            "info": {
                "live_stats": container_info.get("live_stats", {}),
                "container": {
                    "status": "up" if container_info.get("status") == "running" else "down",
                },
                "endpoint": {
                    "status": "up" if exchange_endpoint_status["services"]["online"] else "down",
                }
            }
        })

    for each_container in monitoringInfos:
        process_container(each_container)

    return jsonify(exchange_service_status)


if __name__ == "__main__":
    app.run(port=4006, debug=True)
