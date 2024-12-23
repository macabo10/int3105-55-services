import redis
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
        "container_name": "gold_price_service_no1",
        "REDIS_PORT": 6380
    },
    {
        "container_name": "gold_price_service_no2",
        "REDIS_PORT": 6381
    },
    {
        "container_name": "gold_price_service_no3",
        "REDIS_PORT": 6388
    }
]


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


def get_metrics(host, port):
    def connect_to_redis(host, port):
        redis_host = host
        redis_port = port
        for _ in range(10):  # Retry connecting to Redis up to 10 times
            try:
                client = redis.StrictRedis(
                    host=redis_host, port=redis_port, decode_responses=True)
                if client.ping():
                    print("Connected to Redis!")
                    return client
            except redis.ConnectionError:
                print("Redis is not ready yet. Retrying in 5 seconds...")
                time.sleep(5)
        raise Exception("Failed to connect to Redis after multiple attempts")

    redis_client = connect_to_redis(host, port)
    incoming_requests = redis_client.get("incoming_requests") or 0
    outgoing_responses = redis_client.get("outgoing_responses") or 0

    redis_client.delete("incoming_requests")
    redis_client.delete("outgoing_responses")

    return json.dumps({
        "incoming_requests": int(incoming_requests),
        "outgoing_responses": int(outgoing_responses)
    })


@app.route('/', methods=['GET'])
@cross_origin()
def health_check():
    gold_service_status = []
    threads = []

    def process_container(each_container):
        container_name = each_container["container_name"]

        # Initialize with default value
        container_info = {"error": "Failed to retrieve container stats"}

        try:
            container_info = get_container_stats(container_name)
        except Exception as e:
            print(f"Failed to get container status: {e}")

        user_capacity = json.loads(get_metrics(
            'localhost', each_container["REDIS_PORT"]))

        gold_service_status.append({
            "container_name": container_name,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() + 7*3600)),
            "created_at": container_info.get("created"),
            "info": {
                "live_stats": container_info.get("live_stats", {}),
                "container": {
                    "status": "up" if container_info.get("status") == "running" else "down",
                },
                "user_capacity": user_capacity
            }
        })

    for each_container in monitoringInfos:
        thread = threading.Thread(
            target=process_container, args=(each_container,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return jsonify(gold_service_status)


if __name__ == "__main__":
    app.run(port=4007, debug=True)
