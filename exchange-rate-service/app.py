from flask import Flask, jsonify, make_response, request
from flask_cors import CORS, cross_origin

from exchange_rate_service import get_exchange_rate

app = Flask(__name__)
cors = CORS(app)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3006)