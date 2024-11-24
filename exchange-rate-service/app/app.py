import redis
import os
import pika
import time
from exchange_rate_service import get_exchange_rate
from flask import Flask, jsonify, make_response, request
import json

app = Flask(__name__)


def connect_to_redis():
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    for _ in range(10):  # Retry connecting to Redis up to 10 times
        try:
            client = redis.StrictRedis(
                host=redis_host, port=redis_port, decode_responses=True)
            if client.ping():
                print("Connected to Redis!")
                return client
        except redis.ConnectionError:
            print("Redis is not ready yet. Retrying in 5 seconds...")
            time.sleep(5)
    raise Exception("Failed to connect to Redis after multiple attempts")


redis_client = connect_to_redis()


def increment_metric(metric_name):
    redis_client.incr(metric_name)


def on_request(ch, method, properties, body):
    increment_metric("incoming_requests")
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
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id),
            body=json.dumps(response)
        )
        increment_metric("outgoing_responses")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return


def start_rpc_server():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('172.30.0.2'))
    channel = connection.channel()

    channel.queue_declare(queue='exchange_rate_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='exchange_rate_queue',
                          on_message_callback=on_request)

    print(" [x] Awaiting RPC requests")
    channel.start_consuming()


if __name__ == "__main__":
    start_rpc_server()
