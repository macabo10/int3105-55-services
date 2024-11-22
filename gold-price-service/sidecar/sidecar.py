import json
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import requests
import subprocess
import time
import threading
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__)
cors = CORS(app)

monitoringInfos = [
    {
        "container_name": "gold_price_service_no1",
        "API": "http://localhost:3008/"
    },
    {
        "container_name": "gold_price_service_no2",
        "API": "http://localhost:3009/"
    }
]


def send_email_notification(container_name):
    sender_email = "pixelend2003@yahoo.com.vn" 
    receiver_email = "daavenspicks@gmail.com" 
    app_password = "pdajertdwxleoqfu"

    # Nội dung mail
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Container {container_name} Status Alert"
    message["From"] = sender_email
    message["To"] = receiver_email
    text = f"The container {container_name} is down."
    part = MIMEText(text, "plain")
    message.attach(part)

    try:
        # Đoạn này kết nối các thứ r gửi mail đi
        with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as server:
            server.set_debuglevel(1)
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Email sent to {receiver_email} about container {container_name}")
    except Exception as e:
        print(f"Failed to send email: {e}")


def check_service(url):
    try:
        payload = {"gold_type": "vang24k"}
        response = requests.post(url, json=payload, timeout=1)
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
    gold_service_status = []
    threads = []

    def process_container(each_container):
        container_name = each_container["container_name"]
        api = each_container["API"]
        global gold_endpoint_status
        report = endpoint_health_check(api)
        if report:
            gold_endpoint_status = report
            print("Updated gold_endpoint_status:", gold_endpoint_status)
        else:
            print("Warning: Received empty or invalid report")

        # Initialize with default value
        container_info = {"error": "Failed to retrieve container stats"}

        try:
            container_info = get_container_stats(container_name)
        except Exception as e:
            print(f"Failed to get container status: {e}")

        gold_service_status.append({
            "container_name": container_name,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() + 7*3600)),
            "created_at": container_info.get("created"),
            "info": {
                "live_stats": container_info.get("live_stats", {}),
                "container": {
                    "status": "up" if container_info.get("status") == "running" else "down",
                },
                "endpoint": {
                    "status": "up" if gold_endpoint_status["services"]["online"] else "down",
                }
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

def check_container_status(container):
    container_name = container["container_name"]
    inspect_cmd = f"docker inspect {container_name}"
    try:
        inspect_result = subprocess.run(inspect_cmd, shell=True, capture_output=True, text=True, check=True)
        inspect_data = json.loads(inspect_result.stdout)[0]
        status = inspect_data["State"]["Status"]
        if status == "running":
            return True
        else: 
            return False
    except requests.exceptions.RequestException:
        return False


def monitor_containers():
    while True:
        for container in monitoringInfos:
            status = check_container_status(container)
            if status == False:
                send_email_notification(container["container_name"])
        time.sleep(60)

if __name__ == "__main__":
    monitoring_thread = threading.Thread(target=monitor_containers)
    monitoring_thread.daemon = True
    monitoring_thread.start()
    app.run(port=4007, debug=True)
