import pika
import time
import requests
from exchange_rate_service import get_exchange_rate
from flask import Flask, jsonify, make_response, request
import json

app = Flask(__name__)

def on_request(ch, method, properties, body):
    request = body.decode('utf-8')
    
    data = json.loads(request)
    print(data)
    # Check if the request body is empty or missing the gold_type field
    if not data or 'currency' not in data:
        return make_response(jsonify({"error": "Bad Request"}), 400)
    
    currency = data["currency"]
    print(f"Getting exchange rate for {currency}")

    result = get_exchange_rate(currency)

    if result is not None:
        print(f"Exchange rate for {currency} is: {result}")
        response = {
            "currency": currency,
            "exchange_rate": result
        }
        ch.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=json.dumps(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    

def start_rpc_server():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='exchange_rate_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='exchange_rate_queue', on_message_callback=on_request)

    print(" [x] Awaiting RPC requests")
    channel.start_consuming()

if __name__ == "__main__":
    start_rpc_server()
