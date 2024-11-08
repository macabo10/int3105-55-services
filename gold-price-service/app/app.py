from gold_price_service import get_gold_price
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS, cross_origin
# import time
# from threading import Thread

app = Flask(__name__)
cors = CORS(app)

@app.route('/', methods=['POST'])
@cross_origin()
# handles the incoming POST requests
def handle():
    print(request.json)
    # Check if the request is JSON
    if request.content_type != 'application/json':
        return make_response(jsonify({"error": "Unsupported Media Type"}), 415)

    data = request.get_json()
    # Check if the request body is empty or missing the gold_type field
    if not data or 'gold_type' not in data:
        return make_response(jsonify({"error": "Bad Request"}), 400)

    gold_type = data["gold_type"]
    print(f"Getting buy price for {gold_type}")

    result = get_gold_price(gold_type)

    if result is not None:
        print(f"Price for {gold_type} is: {result}")
        return make_response(jsonify({"gold_price": result}), 200)

    return make_response(jsonify({"error": "Gold type not found"}), 404)

if __name__ == "__main__":
    # Run the Flask app, listening on port 3000 by default
    # Thread(target=health_check_thread, daemon=True).start()
    app.run(host='0.0.0.0', port=3007)