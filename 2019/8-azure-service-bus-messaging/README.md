# Application messaging with Azure Service Bus

Azure Service Bus is a way to pass messages between applications and services - it doesn't matter where
these applications are hosted or even if they're associated with an Azure account, as long as they have
authorization to connect to the Service Bus system with a token. This lab covers using Service Bus as a
queue messaging system, but it also supports a Publish/Subscribe.

In this lab you will:

- Use the Azure CLI to create resources and get configuration values
- Write a small application which passes messages over a Service Bus queue

> __IMPORTANT__: Azure CLI instructions here are written for the `bash` shell, but the Azure CLI
> is cross-platform and will also work in Windows CMD, PowerShell 5.1, or PowerShell 6.x. Choose
> the shell that's most comfortable for you. Where UNIX-specific features are used, an alternative
> for PowerShell is shown.

## Create the resources in Azure

For this lab at PyCon, we've assigned you a subscription to create resources in and have already logged
you in so you can create resources right away.

The first step is to create a resource group, which functions as a logical container within Azure to
group resources together:

```bash
# RESOURCE_GROUP='Group-...'
RESOURCE_GROUP=$(az group list | jq -r '[.[].name|select(. | startswith("Group-"))][0]')
az group create --name $RESOURCE_GROUP --location westus2
```

Next, create the Service Bus and queue. Service Bus resources are separate from their messaging
systems, so one Service Bus can host multiple different queues and publishing topics.

Since service bus names must be unique, a random string of characters is added onto the end of it:

> bash

```bash
busName="PyconLabBus$(openssl rand -hex 3)"
az servicebus namespace create --name $busName --resource-group $RESOURCE_GROUP
az servicebus queue create --name PyconLabQueue --resource-group $RESOURCE_GROUP --namespace-name $busName
```

> PowerShell

```powershell
$busName="PyconLabBus$((((New-Guid).Guid) -split '-')[0])"
az servicebus namespace create --name $busName --resource-group $RESOURCE_GROUP
az servicebus queue create --name PyconLabQueue --resource-group $RESOURCE_GROUP --namespace-name $busName
```

In order to access the queue to send and receive messages, you need the queue endpoint and a token to
connect. The CLI allows getting both:

```bash
accessRule=$(az servicebus namespace authorization-rule list --namespace-name $busName \
    --resource-group $RESOURCE_GROUP \
    --query '[0].name' \
    --output tsv)
export SB_CONNECTION=$(az servicebus namespace authorization-rule keys list \
    --resource-group $RESOURCE_GROUP \
    --namespace-name $busName \
    --name $accessRule \
    --query 'primaryConnectionString' \
    --output tsv)
```

Now that the queue is set up and you have the connection string, it's time to create the application.

## Application setup

The application you'll create to connect to the messaging queue will be a small Flask app that
has two API endpoints: One to send messages to the queue, and one to receive messages. In a new
file called `app.py`, begin with the code:

```python
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

sb_client = ServiceBusClient.from_connection_string(os.environ['SB_CONNECTION'])
queue = sb_client.get_queue('PyconLabQueue')

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
```

In addition to importing modules, this code:

- Ensures that the environment value for `SB_CONNECTION` is available
- Sets up a Service Bus client, and gets an object representing the messaging queue from it
- Configures the Flask application

## Send messages to the queue

Next, add a route to the application which will provide the endpoint for sending messages:

```python
@app.route('/send', methods=['POST'])
def send():
    message = request.get_data(cache=False, as_text=True)
    app.logger.info(f'SEND: {message}')
    (success, __) = queue.send(Message(message))[0]
    return str(success)
```

This simple method demonstrates the ease of creating and sending a message over the queue. It:

- Gets the request body data as a string
- Creates a new message and sends it to the queue
- Returns a value showing whether or not the message was added to the queue

Now that there's a way to send messages to the queue, it's time to run a test. Start
the flask app:

```bash
export FLASK_ENV=development
flask run
```

The output will show you that a server is running at `127.0.0.1:5000`. To send a message, you will need to send a `POST` request to `http://localhost:5000/send`. Do this with the `curl` command in a new terminal:

```bash
curl -XPOST --data 'Hello world!' http://localhost:5000/send
```

When sending the message, you should also see an `INFO` logging notice in the Flask application which indicates
that the message was received, and the message contents:

```output
[...] INFO in app: SEND: Hello world!
```

This will put a message into the queue. Although the CLI doesn't allow you to inspect message contents,
it does allow you to see what the current state of the queue is. Check and make sure that the message
was added to the queue now:

```bash
az servicebus queue show --name PyconLabQueue \
    --namespace-name $busName \
    --resource-group $RESOURCE_GROUP \
    --query 'countDetails.activeMessageCount'
```

You should see that there is `1` message in the queue.

## Retrieve messages from the queue

Next, add a route to the application for retrieving messages:

```python
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
```

This method is more complicated than the send operation. It:

- Gets a message receiver for the queue, which will time out on retrieving messages after 3 seconds. This receiver will pull *all* messages available in the queue until the end of the timeout.
- The received messages are iterated over, and:
  - Converted from a bytestream to a string
  - Marked as `Completed` so that they can be removed from the queue
- Responds with a JSON array containing all of the received messages

Now send a `GET` request with the `curl` command to get the message in the queue:

```bash
curl -XGET http://localhost:5000/receive

["Hello world!"]
```

Note that this request takes the full 3 seconds of the receiver timeout to respond. This is because
the `get_receiver()` method is blocking. There are non-blocking and other types of batching receivers
available, which you're encouraged to explore.

You can also check the queue contents again with the same command used to inspect the queue in the last step, and see that the message has been processed.

## Play around with the message send/receive

To learn more about how service bus queues operate, go ahead and try:

- Sending more than one message before calling the `/receive` endpoint.
- Changing the `idle_timeout` value to be longer, then calling the `/receive` endpoint before sending a message. Before it returns, send a message to the `/send` endpoint.

The `get_receiver()` call is also blocking, but there are ways to work around this and use
a receiver to only get and complete a maximum (or minimum) number of messages from the queue. Look at the
[ReceiveClientMixin API documentation](https://docs.microsoft.com/en-us/python/api/azure-servicebus/azure.servicebus.servicebus_client.receiveclientmixin?view=azure-python) and think about ways to play around
with it to get non-blocking behavior, ways to process individual messages, skip messages, or change other behavior.

> __HINT__: The `ReceiveClientMixin.peek()` and `Receiver.fetch_next()` methods will be of interest when
> investigating other ways to handle message processing. You'll also want to take a look at the
> `prefetch` parameter of `ReceiveClientMixin.get_receiver()`.
