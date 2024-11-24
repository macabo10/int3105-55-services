import redis
import os
import time
from flask import Flask, request, jsonify
import pika
import json
import uuid
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
import threading

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000/second"],
    storage_uri="memory://",
)

# Thread-local storage for RpcClient instances
thread_local = threading.local()


class RpcClient:
    def __init__(self):
        self.callback_queue = None
        self.response = None
        self.corr_id = None

    def connect(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('172.30.0.2'))
        channel = connection.channel()
        result = channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        channel.basic_consume(queue=self.callback_queue,
                              on_message_callback=self.on_response, auto_ack=True)
        return connection, channel

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def call(self, request_data, queue_name, priority=0):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        connection, channel = self.connect()
        try:
            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.corr_id,
                    priority=priority,
                    delivery_mode=2  # Make message persistent
                ),
                body=json.dumps(request_data)
            )
            while self.response is None:
                connection.process_data_events()
            return self.response
        except (pika.exceptions.ChannelWrongStateError, pika.exceptions.AMQPConnectionError, pika.exceptions.StreamLostError) as e:
            print(f"Connection error: {e}, reconnecting...")
            connection.close()
            return self.call(request_data, queue_name)
        finally:
            connection.close()


def get_rpc_client():
    if not hasattr(thread_local, 'rpc_client'):
        thread_local.rpc_client = RpcClient()
    return thread_local.rpc_client


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


@app.errorhandler(RateLimitExceeded)
def handle_rate_limit_exceeded(e):
    increment_metric("incoming_requests")
    return jsonify(error="rate limit exceeded", message=str(e.description)), 429


@app.route('/get_exchange_rate', methods=['POST'])
@limiter.limit("1000/second")
def get_exchange_rate():
    increment_metric("incoming_requests")
    data = request.json
    if 'priority' in data:
        priority = data['priority']
    else:
        priority = 0
    rpc_client = get_rpc_client()
    response = rpc_client.call(data, 'exchange_rate_queue', priority=priority)
    increment_metric("outgoing_responses")
    return jsonify(response), 200


@app.route('/get_gold_price', methods=['POST'])
@limiter.limit("1000/second")
def get_gold_price():
    increment_metric("incoming_requests")
    data = request.json
    if 'priority' in data:
        priority = data['priority']
    else:
        priority = 0
    rpc_client = get_rpc_client()
    response = rpc_client.call(data, 'gold_price_queue', priority=priority)
    increment_metric("outgoing_responses")
    return jsonify(response), 200


if __name__ == "__main__":
    app.run(port=4000, threaded=True)
