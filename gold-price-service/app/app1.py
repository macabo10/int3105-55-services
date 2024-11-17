import pika
import time
import requests
from gold_price_service import get_gold_price
from flask import Flask, jsonify, make_response, request
import json

app = Flask(__name__)

def callback(ch, method, properties, body):
    request = body.decode('utf-8')
    
    data = json.loads(request)
    # data = request.get_json()
    print(data)
    # Check if the request body is empty or missing the gold_type field
    if not data or 'gold_type' not in data:
        return make_response(jsonify({"error": "Bad Request"}), 400)
    
    gold_type = data["gold_type"]
    print(f"Getting buy price for {gold_type}")

    result = get_gold_price(gold_type)

    if result is not None:
        print(f"Price for {gold_type} is: {result}")
        return requests.post('http://localhost:5001/receive_gold_price', json={"gold_price": result})
    

def start_consuming():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='gold_price_queue')

    channel.basic_consume(queue='gold_price_queue', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == "__main__":
    start_consuming()

