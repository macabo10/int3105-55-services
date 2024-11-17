from flask import Flask, request, jsonify
import pika
import json

app = Flask(__name__)

def send_to_exchange_rate_service(request, queue_name='exchange_rate_queue'):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(request),
        properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)
        )
    
    connection.close()


@app.route('/get_exchange_rate', methods=['POST'])
def get_exchange_rate():
    data = request.json
    send_to_exchange_rate_service(data)
    return jsonify({"status": "Request received and sent to Exchange Rate Service"}), 202

@app.route('/receive_exchange_rate', methods=['POST'])
def receive_exchange_rate():
    # This would be called by Exchange Rate Service
    exchange_rate = request.json
    return jsonify({"status": "Exchange Rate received", "data": exchange_rate}), 200

@app.route('/get_gold_price', methods=['POST'])
def get_gold_price():
    data = request.json
    send_to_exchange_rate_service(data, 'gold_price_queue')
    return jsonify({"status": "Request received and sent to Gold Price Service"}), 202

@app.route('/receive_gold_price', methods=['POST'])
def receive_gold_price():
    # This would be called by Gold Price Service
    gold_price = request.json
    return jsonify({"status": "Gold Price received", "data": gold_price}), 200

if __name__ == "__main__":
    app.run(port=5001)

