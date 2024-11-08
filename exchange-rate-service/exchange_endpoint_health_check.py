import requests
from flask import jsonify


def check_service(url):
    try:
        payload = {"currency": "USD"}
        response = requests.post(url, json=payload, timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def endpoint_health_check():
    endpoint_status = {
        "exchange_rate_api_online": check_service("http://localhost:3006/"),
    }
    # Return a regular dictionary instead of using jsonify
    return {"services": endpoint_status}