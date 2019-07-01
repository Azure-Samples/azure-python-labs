import os
import sys
import json
import logging

from flask import Flask, request, make_response
from azure.servicebus import ServiceBusClient, Message

connection_string = os.environ.get('SB_CONNECTION')
if connection_string is None:
    print('ERROR: Requires `SB_CONNECTION` value to be set', file=sys.stderr)
    sys.exit(1)

sb_client = ServiceBusClient.from_connection_string(
    os.environ['SB_CONNECTION'])
queue = sb_client.get_queue('PyconLabQueue')

app = Flask(__name__)
app.logger.setLevel(logging.INFO)


@app.route('/send', methods=['POST'])
def send():
    message = request.get_data(cache=False, as_text=True)
    app.logger.info(f'SEND: {message}')
    (success, __) = queue.send(Message(message))[0]
    return str(success)


@app.route('/receive', methods=['GET'])
def get():
    receiver = queue.get_receiver(idle_timeout=3)
    messages = []
    for message in receiver:
        app.logger.info(f'Got message: {message}')
        messages.append(str(message))
        message.complete()
    return make_response(json.dumps(messages), {
        'Content-Type': 'application/json; charset=utf-8'
    })
