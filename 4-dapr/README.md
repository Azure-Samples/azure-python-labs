# Explore the Distributed Application Runtime (Dapr) with Python

Dapr is a portable, serverless, event-driven runtime that makes it easy for developers to build resilient, stateless and stateful microservices that run on the cloud and edge and embraces the diversity of languages and developer frameworks.

You can learn more about Dapr at [dapr.io](https://dapr.io), [github.com/dapr/dapr](https://github.com/dapr/dapr), [@dapr (twitter.com)](https://twitter.com/dapr), the [Dapr Discord](https://aka.ms/dapr-discord),  [Introducing Dapr (2:27) (youtube.com)](https://youtu.be/9o9iDAgYBA8) and [aka.ms/hello-dapr](https://aka.ms/hello-dapr).

Dapr was announced in [October 2019](https://cloudblogs.microsoft.com/opensource/2019/10/16/announcing-dapr-open-source-project-build-microservice-applications/) and [reached v1.0 in February 2021](https://blog.dapr.io/posts/2021/02/17/announcing-dapr-v1.0/), is now [v1.1.0](https://twitter.com/daprdev/status/1378015524672704512?s=20), and has over 13.1k GitHub stars as of May 2021. It is used in production by customers including [ZEISS](https://customers.microsoft.com/en-us/story/1336089737047375040-zeiss-accelerates-cloud-first-development-on-azure-and-streamlines-order-processing), [Ignition Group](https://customers.microsoft.com/en-us/story/1335733425802443016-ignition-group-speeds-development-and-payment-processing-using-dapr-and-azure), [Roadwork](https://blog.dapr.io/posts/2021/02/09/running-dapr-in-production-at-roadwork/), [Alibaba Cloud](https://blog.dapr.io/posts/2021/03/19/how-alibaba-is-using-dapr/) and many more.


Dapr uses a [sidecar architecture](https://docs.dapr.io/concepts/overview/#sidecar-architecture), as a simple process, or in a container (with or without Kubernetes), to provide [microservice building blocks](https://docs.dapr.io/concepts/overview/#microservice-building-blocks-for-cloud-and-edge) for cloud and edge that include:

- [Service invocation](https://docs.dapr.io/developing-applications/building-blocks/service-invocation/): Perform direct, secure, service-to-service method calls
- [State management](https://docs.dapr.io/developing-applications/building-blocks/state-management/): Create long running stateful services
- [Publish & subscribe messaging](https://docs.dapr.io/developing-applications/building-blocks/pubsub/): Secure, scalable messaging between services
- [Bindings](https://docs.dapr.io/developing-applications/building-blocks/bindings/): Interface with or be triggered from external systems
- [Actors](https://docs.dapr.io/developing-applications/building-blocks/actors/): Encapsulate code and data in reusable actor objects as a common microservices design pattern
- [Observability](https://docs.dapr.io/developing-applications/building-blocks/observability/): See and measure the message calls across components and networked services
- [Secrets management](https://docs.dapr.io/developing-applications/building-blocks/secrets/): Securely access secrets from your application

Dapr uses [Components](https://docs.dapr.io/concepts/components-concept/) for State stores, Service discovery, Middleware, Pub/sub brokers, Bindings, and Secret stores. These include both self-hosted, open source, and managed platforms across multiple clouds. They enable your application to be portable across local development, on-premesis and cloud environments.

Dapr can be used via HTTP, gRPC, and language-specific SDKs for languages inlcuding .NET, Python, Java, Go, PHP, C++, Rust and JavaScript


## What you will learn

You will:
- Get hands-on with Dapr by running it on your local machine through the [Try Dapr](https://docs.dapr.io/getting-started/) experience.
- Explore State Mangement and Secrets building blocks via the REST API using cURL (optional), Python Requests, and the Dapr SDK for Python ([dapr/python-sdk](https://github.com/dapr/python-sdk)).
- Seamlessly swap the State component from local development to a managed service in the cloud. 

## Prerequisites
- You will need [Docker](https://docs.docker.com/get-docker/) to use this lab as-is with Dapr's default Docker support. Dapr can run as a binary [in self-hosted mode without Docker](https://docs.dapr.io/operations/hosting/self-hosted/self-hosted-no-docker/), however it will require additional setup steps.
- [Python 3](https://www.python.org/downloads/)

## Try Dapr

In order to use Dapr locally you will need to install the Dapr CLI and local components using 

### [1. Install the Dapr CLI](https://docs.dapr.io/getting-started/install-dapr-cli/)

Install the Dapr CLI on macOS, Windows or Linux via the above link.

### [2. Initialize Dapr](https://docs.dapr.io/getting-started/install-dapr-selfhost/)

Initialize Dapr using the `dapr init` command. This step assumes we are using [Docker](https://docs.docker.com/get-docker/).

### [3. Use the Dapr API](https://docs.dapr.io/getting-started/get-started-api/)

We will now run the dapr sidecar using the dapr CLI:

```bash
dapr run --app-id myapp --dapr-http-port 3500
```

Congratulations, you will now have REST API for the automatically configured [State management](https://docs.dapr.io/developing-applications/building-blocks/state-management/state-management-overview/) building block available via HTTP on `http://localhost:3500/v1.0/state/statestore`

You can do a quick test by running the following to save and get some state:

```bash
# save state
curl -X POST -H "Content-Type: application/json" -d '[{ "key": "name", "value": "Bruce Wayne"}]' http://localhost:3500/v1.0/state/statestore`
# get state
curl http://localhost:3500/v1.0/state/statestore/name
```

Instead of using bash (`curl`) or PowerShell (`Invoke-RestMethod`), we can continue to explore it with Python using both [Python Requests](https://docs.python-requests.org/en/master/) against the REST API, and the [Dapr SDK for Python (dapr/python-sdk)](https://github.com/dapr/python-sdk).

### 3.1. Install requirements for CLI

Install [Python Fire](https://github.com/google/python-fire#installation), [Python Requests](https://docs.python-requests.org/en/master/user/install/#install) and the [Dapr SDK for Python](https://github.com/dapr/python-sdk#install-dapr-python-sdk)

```bash
# clone this repository locally
git clone https://github.com/Azure-Samples/azure-python-labs.git

# cd into the correct directory
cd 4-dapr

# create and activate a virtual environment
python3 -m venv env
source env/bin/activate

# install dependencies
pip install -r requirements.txt
```

### 3.2 Get and set state via Python Requests and the Dapr SDK for Python

Let's start (or restart) our dapr sidecar in its own terminal window, but this time in addition to the HTTP port for curl and Python Requests, we will also need to provide a gRPC port for the Python SDK which uses gRPC by default and [defaults to port 50001](https://github.com/dapr/python-sdk/blob/master/dapr/conf/global_settings.py#L16):

```bash
dapr run --app-id myapp --dapr-http-port 3500 --dapr-grpc-port 50001
```

Now if we run `python main.py` in another terminal window we can see the list of commands (see: [help.txt](help.txt)).

Explore [main.py](main.py) and the `# http examples` and `# sdk examples`:

```python
# http examples
def dapr_http_get_state(store="statestore", name="name"):
    """GET /v1.0/state/{store}/{name}"""
    port = os.getenv("DAPR_HTTP_PORT") or "3500"
    r = requests.get(f"http://localhost:{port}/v1.0/state/{store}/{name}")
    print(r.json())

# ...

# sdk examples
def dapr_get_state(store="statestore", name="name"):
    """DaprClient().get_state(store_name=store, key=name)"""
    with dapr.clients.DaprClient() as d:
        # Wait for sidecar to be up within 5 seconds.
        d.wait(5)
        res = d.get_state(store_name=store, key=name)
        print(res.data.decode())s
```

You can execute these as follows:

```bash
# get state with requests over http
python main.py dapr_http_get_state
# get state with sdk over grpc
python main.py dapr_get_state
```

We can override parameters as follows, and use the `--help` flag to view help text (example: [help_dapr_http_get_state.txt](help_dapr_http_get_state.txt)) including the parameters you can use.

```bash
# get help text
python main.py dapr_save_state --help

python main.py dapr_http_post_state --store="statestore" --name="me" --value="hello" 

python main.py dapr_http_get_state --name "me"

python main.py dapr_save_state --store="statestore" --name="me" --value="world" 

python main.py dapr_get_state --store="statestore" --name="me"
```

### 3.3 Explore the Secret building block

Another building block we will explore is [Secrets](https://docs.dapr.io/developing-applications/building-blocks/secrets/secrets-overview/).

We are going to use the [Local file](https://docs.dapr.io/developing-applications/building-blocks/secrets/howto-secrets/#set-up-a-secret-store) secret store which we have pre-configured in [my-components/localSecretStore.yaml](my-components/localSecretStore.yaml) with secrets stored in [my-secrets.json](my-secrets.json).

In order to reference the [components](https://docs.dapr.io/concepts/components-concept/) configured in `my-components`, we will need to pass the `--components-path` flag when we run the dapr sidecar.

In your first terminal, run:

```bash
cd 4-dapr

dapr run --app-id myapp --dapr-http-port 3500 --dapr-grpc-port 50001 --components-path ./my-components
```

In your second terminal, run:

```bash
python main.py dapr_http_get_secret --name "my-secret"
python main.py dapr_get_secret --name "my-secret"
```

> Are you ready to explore further? These SDK snippets were taken directly from the Dapr SDK for Python [examples](https://github.com/dapr/python-sdk/tree/master/examples) and you can copy/paste into your own functions in `main.py`. We'd also love to hear your feedback on the SDK, the examples, and how you use Dapr with Python!

Now you have used Dapr with Python via the HTTP API and the Dapr SDK for Python, you may wish to continue the [Try Dapr](https://docs.dapr.io/getting-started/) experience to "Configure a component" and "Explore Dapr quickstarts".

### [4. Configure a component](https://docs.dapr.io/getting-started/get-started-component/)

### [5. Explore Dapr quickstarts](https://docs.dapr.io/getting-started/quickstarts/)

## Optional Challenge: Send your state to the cloud with Azure Blob Storage 

Can you take your [state store](https://docs.dapr.io/developing-applications/building-blocks/state-management/state-management-overview/) to the Cloud with Azure Blob Storage? Your above code will require zero changes! Here are some hints:

- [State stores (docs.dapr.io)](https://docs.dapr.io/reference/components-reference/supported-state-stores/#microsoft-azure)
- [Create a storage account (docs.microsoft.com)](https://docs.microsoft.com/azure/storage/common/storage-account-create?tabs=azure-portal)
- We have pre-configured a component under [az-components/state-azure-blobstorage.yml](az-components/state-azure-blobstorage.yml)
- The component also uses a [secretKeyRef](https://docs.dapr.io/operations/components/component-secrets/#referencing-secrets) to keep the `accountKey` out of your component YAML, but retrieve it from [az-secrets.json](az-secrets.json). 
- Note: in production you would likely use [Azure Key Vault](https://docs.dapr.io/reference/components-reference/supported-secret-stores/azure-keyvault/) for secret storage, but we only want you to send your state to the cloud right now.

