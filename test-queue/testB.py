# service_b.py
from flask import Flask, request, jsonify
import pika
import json

app = Flask(__name__)

def send_to_service_c(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='service_c_queue')

    channel.basic_publish(exchange='', routing_key='service_c_queue', body=json.dumps(data))
    connection.close()

@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    send_to_service_c(data)
    return jsonify({"status": "Request received and sent to Service C"}), 202

@app.route('/receive_results', methods=['POST'])
def receive_results():
    # This would be called by Service C
    results = request.json
    return jsonify({"status": "Results received", "data": results}), 200

if __name__ == "__main__":
    app.run(port=5001)