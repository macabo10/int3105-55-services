# FILE: send_single_request.py
import requests
import json
import time

def send_request():
    url = 'http://localhost:5002/get_gold_price'
    headers = {'Content-Type': 'application/json'}
    request_data = {
        "gold_type": "vang24k"
    }
    
    for i in range(10):
        print("hello")
        try:
            response = requests.post(url, headers=headers, data=json.dumps(request_data))
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            response_data = response.json()  # Attempt to parse the response as JSON
            print(f"Response {i+1}: {response_data}")
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred on request {i+1}: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred on request {i+1}: {req_err}")
        except json.JSONDecodeError as json_err:
            print(f"JSON decode error on request {i+1}: {json_err}")

if __name__ == "__main__":
    send_request()