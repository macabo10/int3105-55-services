from flask import Flask, request, jsonify
import pika
import json
import uuid
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100/second"],
    storage_uri="memory://",
)

class RpcClient:
    def __init__(self):
        self.callback_queue = None
        self.response = None
        self.corr_id = None

    def connect(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        result = channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)
        return connection, channel

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def call(self, request_data, queue_name):
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

rpc_client = RpcClient()

@app.errorhandler(RateLimitExceeded)
def handle_rate_limit_exceeded(e):
    return jsonify(error="rate limit exceeded", message=str(e.description)), 429

@app.route('/get_exchange_rate', methods=['POST'])
@limiter.limit("1000/second")
def get_exchange_rate():
    data = request.json
    response = rpc_client.call(data, 'exchange_rate_queue')
    return jsonify(response), 200

@app.route('/get_gold_price', methods=['POST'])
@limiter.limit("1000/second")
def get_gold_price():
    data = request.json
    response = rpc_client.call(data, 'gold_price_queue')
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(port=4000, threaded=True)