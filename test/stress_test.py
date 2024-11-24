# FILE: send_requests.py
import requests
import json
from concurrent.futures import ThreadPoolExecutor

def send_request(data):
    # url = 'http://localhost:4000/get_gold_price'
    url = 'http://localhost:4000/get_exchange_rate'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def main():
    request_data = {
        # "gold_type": "vang24k"
        "currency": "USD"
    }

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(send_request, request_data) for _ in range(100)]
        for future in futures:
            try:
                response = future.result()
                print(response)
            except Exception as e:
                print(f"Request failed: {e}")

if __name__ == "__main__":
    main()