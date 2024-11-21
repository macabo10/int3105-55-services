# service_c.py
from flask import Flask, request, jsonify
import pika
import json
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=5)

def process_data(data):
    # Simulate processing
    return f"Processed {data['data']}"

def callback(ch, method, properties, body):
    data = json.loads(body)
    result = process_data(data)
    send_results_to_service_b(result)

def send_results_to_service_b(result):
    response = requests.post("http://localhost:5001/receive_results", json={"result": result})
    print(f"Response from Service B: {response.json()}")

def start_consuming():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='service_c_queue')

    channel.basic_consume(queue='service_c_queue', on_message_callback=callback, auto_ack=True)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    start_consuming()