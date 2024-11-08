from flask import Flask, jsonify, make_response, request
from flask_cors import CORS, cross_origin
from exchange_endpoint_health_check import endpoint_health_check
from exchange_rate_service import get_exchange_rate
import time
from threading import Thread

app = Flask(__name__)
cors = CORS(app)

latest_exchange_health_report = {}

@app.route('/', methods=['POST'])
@cross_origin()
def handle():
    # Check if the request is JSON
    if request.content_type != 'application/json':
        return make_response(jsonify({"error": "Unsupported Media Type"}), 415)
    
    data = request.get_json()
    # Check if the request body is empty or missing the currency field
    if not data or 'currency' not in data:
        return make_response(jsonify({"error": "Bad Request"}), 400)

    currency = data["currency"]

    # Capitalize the currency code
    currency = currency.upper()

    print(f"Getting exchange rate for {currency}")
    result = get_exchange_rate(currency)

    if result is not None:
        print(f"Exchange rate: {result}")
        return make_response(jsonify({"exchange_rate": result}), 200)
    
    return make_response(jsonify({"error": "Currency not found"}), 404)

@app.route('/exchange-health-check', methods=['GET'])
def health_check():
    return jsonify(latest_exchange_health_report)

def health_check_thread():
    global latest_exchange_health_report
    print("Health check thread started.")
    while True:
        report = endpoint_health_check()
        if report:
            latest_exchange_health_report = report
            print("Updated latest_exchange_health_report:", latest_exchange_health_report)
        else:
            print("Warning: Received empty or invalid report")
        time.sleep(10)

if __name__ == "__main__":
    Thread(target=health_check_thread, daemon=True).start()
    app.run(host="0.0.0.0", port=3006)
