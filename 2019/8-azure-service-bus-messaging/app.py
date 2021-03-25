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

queue_name='PyconLabQueue'
sb_client = ServiceBusClient.from_connection_string(connection_string)
queue_sender = sb_client.get_queue_sender(queue_name)

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.route('/send', methods=['POST'])
def send():
    message = request.get_data(cache=False, as_text=True)
    app.logger.info(f'SEND: {message}')    
    try:
        queue_sender.send_messages(Message(message))
        success = True
    except MessageSendFailed:
        success = False
    return str(success)

@app.route('/receive', methods=['GET'])
def get():
    with sb_client.get_queue_receiver(queue_name, max_wait_time=3) as receiver:
        messages = []
        for message in receiver:
            app.logger.info(f'Got message: {message}')
            messages.append(str(message))
            message.complete()
    return make_response(json.dumps(messages), {
        'Content-Type': 'application/json; charset=utf-8'
        })