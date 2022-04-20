import fire
import requests

import os
import grpc
import dapr.clients

# http examples
def dapr_http_get_state(store="statestore", name="name"):
    """GET /v1.0/state/{store}/{name}"""
    port = os.getenv("DAPR_HTTP_PORT") or "3500"
    r = requests.get(f"http://localhost:{port}/v1.0/state/{store}/{name}")
    print(r.json())

def dapr_http_post_state(store="statestore", name="name", value="Bruce Wayne"):
    """POST /v1.0/state/{store}"""
    port = os.getenv("DAPR_HTTP_PORT") or "3500"
    url1 = f"http://localhost:{port}/v1.0/state/{store}"
    dict1 = [{"key":name, "value": value}]
    r = requests.post(url1, json=dict1)
    print(r.status_code)

def dapr_http_get_secret(store="my-secret-store", name="my-secret"):
    """GET /v1.0/secrets/{store}/{name}"""
    port = os.getenv("DAPR_HTTP_PORT") or "3500"
    r = requests.get(f"http://localhost:{3500}/v1.0/secrets/{store}/{name}")
    print(r.json())

# sdk examples 
def dapr_get_state(store="statestore", name="name"):
    """DaprClient().get_state(store_name=store, key=name)"""
    with dapr.clients.DaprClient() as d:
        # Wait for sidecar to be up within 5 seconds.
        d.wait(5)
        res = d.get_state(store_name=store, key=name)
        print(res.data.decode())

def dapr_save_state(store="statestore", name="hello", value="world"):
    """DaprClient().save_state(store_name=store, key=name, value=value)"""
    with dapr.clients.DaprClient() as d:
        # Wait for sidecar to be up within 5 seconds.
        d.wait(5)
        # Save single state.
        d.save_state(store_name=store, key=name, value=value)
        print(f"State store has successfully saved {value} with {name} as key")

def dapr_save_state_etag(store="statestore", name="hello", value="world", etag=""):
    """DaprClient().save_state(store_name=store, key=name, value=value, etag=etag)"""
    with dapr.clients.DaprClient() as d:
        # Wait for sidecar to be up within 5 seconds.
        d.wait(5)
        if etag == "":
            # Save single state.
            d.save_state(store_name=store, key=name, value=value)
            print(f"State store has successfully saved {value} with {name} as key")
        else:
            # Save with an etag that is different from the one stored in the database.
            try:
                d.save_state(store_name=store, key=name, value=value, etag=etag)
                print(f"State store has successfully saved {value} with {name} as key with etag {etag}")
            except grpc.RpcError as err:
                # StatusCode should be StatusCode.ABORTED.
                print(f"Cannot save due to bad etag. ErrorCode={err.code()}")
                # For detailed error messages from the dapr runtime:
                # print(f"Details={err.details()})

def dapr_get_secret(store="my-secret-store", name="my-secret"):
    """DaprClient().get_secret(store_name=store, key=name)"""
    with dapr.clients.DaprClient() as d:
        # Wait for sidecar to be up within 5 seconds.
        d.wait(5)
        res = d.get_secret(store_name=store, key=name)
        print(res.secret)

# your examples
def test():
    print("hello, test")

if __name__ == '__main__':
    fire.Fire()
