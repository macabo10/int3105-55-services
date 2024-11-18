from flask import Flask, request, jsonify
import pika
import json
import uuid
import threading

app = Flask(__name__)

class RpcClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def call(self, request_data, queue_name):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        try:
            self.channel.basic_publish(
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
                self.connection.process_data_events()
            return self.response
        except pika.exceptions.ChannelWrongStateError as e:
            print(f"Channel wrong state error: {e}, reconnecting...")
            self.reconnect()
            return self.call(request_data, queue_name)
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection error: {e}, reconnecting...")
            self.reconnect()
            return self.call(request_data, queue_name)

    def reconnect(self):
        print("Reconnect...")
        self.connection.close()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)

rpc_client = RpcClient()

@app.route('/get_exchange_rate', methods=['POST'])
def get_exchange_rate():
    data = request.json
    response = rpc_client.call(data, 'exchange_rate_queue')
    return jsonify(response), 200

@app.route('/get_gold_price', methods=['POST'])
def get_gold_price():
    data = request.json
    response = rpc_client.call(data, 'gold_price_queue')
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(port=5002, threaded=True)