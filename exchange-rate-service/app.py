from flask import Flask, jsonify, make_response, request
from flask_cors import CORS, cross_origin

from exchange_rate_service import get_exchange_rate

app = Flask(__name__)
cors = CORS(app)

@app.route('/', methods=['POST'])
@cross_origin()
def handle():
    print(request.json)
    currency = request.json["currency"]

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