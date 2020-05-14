import os
import sys
import json
import logging

from flask import Flask, request, make_response
from azure.servicebus import ServiceBusClient, Message
from azure.servicebus.exceptions import MessageSendFailed

connection_string = os.environ.get('SB_CONNECTION')
if connection_string is None:
    print('ERROR: Requires `SB_CONNECTION` value to be set', file=sys.stderr)
    sys.exit(1)

sb_client = ServiceBusClient.from_connection_string(os.environ['SB_CONNECTION'])
queue_sender = sb_client.get_queue_sender('PyconLabQueue')

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.route('/send', methods=['POST'])
def send():
    message = request.get_data(cache=False, as_text=True)
    app.logger.info(f'SEND: {message}')    
    try:
        queue_sender.send(Message(message))
        success = True
    except MessageSendFailed:
        success = False
    return str(success)

@app.route('/receive', methods=['GET'])
def get():
    receiver = sb_client.get_queue_receiver('PyconLabQueue', idle_timeout=3)
    messages = []
    for message in receiver:
        app.logger.info(f'Got message: {message}')
        messages.append(str(message))
        message.complete()
    return make_response(json.dumps(messages), {
        'Content-Type': 'application/json; charset=utf-8'
        })
