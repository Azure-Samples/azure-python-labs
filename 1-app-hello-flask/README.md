# Containerize and Deploy a Python Flask application with Azure Container Registry and Azure Container Instances

In this lab we will demonstrate how to:
- Build a Python Flask application using Docker and a Dockerfile.
- Build our container image in the cloud using Azure Container Registry (ACR).
- Deploy our container image to Azure Container Instances (ACI).

## 1. Explore Docker and Dockerfiles

This section is **for illustrative purposes only**. If we have Docker installed locally, we have three options to run and/or build our Flask application inside a container:

Run commands manually inside a `python` container pulled from [Docker Hub](https://hub.docker.com/_/python/) to run and debug our application locally.
```bash
git clone https://github.com/Microsoft/python-sample-vscode-flask-tutorial
cd python-sample-vscode-flask-tutorial/
docker run --rm -v ${PWD}:/pwd/ -w /pwd/ -p 8080:5000 -it python bash
pip install -r requirements.txt
export FLASK_APP=startup.py
flask run --host=0.0.0.0
# open http://localhost:8080
```

Build a *development* container from a `Dockerfile` ([dev.Dockerfile](dev.Dockerfile)).
```bash
git clone https://github.com/Microsoft/python-sample-vscode-flask-tutorial
docker build -f dev.Dockerfile -t test python-sample-vscode-flask-tutorial/
docker run --rm -p 8080:5000 -it test
# open http://localhost:8080
```

Build a *production* container from a `Dockerfile` ([prod.Dockerfile](prod.Dockerfile)).
```bash
git clone https://github.com/Microsoft/python-sample-vscode-flask-tutorial
docker build -f prod.Dockerfile -t prod python-sample-vscode-flask-tutorial/
docker run --rm -p 8080:5000 -it prod
# open http://localhost:8080
```

## 2. Build with Azure Container Registry (ACR)

Azure Container Registry is Azure's private container registry. It has the ability to build our container image inside the registry from our source code and a Dockerfile.

In the snippet below we set the correct value for the RESOURCE_GROUP variable. This can be set manually as below, or via the `az group list` command with `jq` to select the name of the "first group that starts with Group-". If you're doing this lab on your own, **not at an event**, you will need to un-comment and **set the RESOURCE_GROUP variable manually**.

Our Azure Container Registry's name must also be globally unique, so we are also setting CONTAINER_REGISTRY to 'acr' with 6 character random suffix.

Let's set our environment variables:

```bash
# RESOURCE_GROUP='Group-...'
RESOURCE_GROUP=$(az group list | jq -r '[.[].name|select(. | startswith("Group-"))][0]')
LOCATION='eastus'
if [ -z "$RANDOM_STR" ]; then RANDOM_STR=$(openssl rand -hex 3); else echo $RANDOM_STR; fi
# RANDOM_STR='9c445c'
CONTAINER_REGISTRY=acr${RANDOM_STR}
CONTAINER_IMAGE='hello-flask:latest'
```

If we're not yet logged in:

    az login

Create the resource group, if required:

    az group create --name $RESOURCE_GROUP --location $LOCATION

Now let's use the Azure CLI (az) to create an Azure Container Registry and build an image in the cloud.

    az acr create -g $RESOURCE_GROUP -l $LOCATION --name $CONTAINER_REGISTRY --sku Basic --admin-enabled true

Next we use the [az acr build](https://docs.microsoft.com/en-us/cli/azure/acr?#az-acr-build) command, which will push our source code and Dockerfile to the cloud, build the image, and store it in our Azure Container Registry:

    az acr build -r $CONTAINER_REGISTRY -t hello-flask --file prod.Dockerfile python-sample-vscode-flask-tutorial/

The fully-qualified name of the image in our Container Registry will then be `$CONTAINER_REGISTRY'.azurecr.io/hello-flask:latest'`. Let's output this with:

    echo "${CONTAINER_REGISTRY}.azurecr.io/hello-flask:latest"

Congratulations, you have built your first image inside Azure Container Registry. This can be used on local and remote machines via `az acr login -n $CONTAINER_REGISTRY` and `docker run -it $CONTAINER_REGISTRY'.azurecr.io/hello-flask:latest'` which we'll explore in a future tutorial.

Since Azure Container Registry (ACR) is completely private, we need to log in with `az acr login` in order to use the image we have built inside our registry. For public images, which we can access without authentication, we can use Docker Hub, where we have pushed a pre-built image available at: `aaronmsft/hello-flask`

Finally, Azure Container Registry enables you to automatically trigger image builds in the cloud [when you commit source code to a Git repository](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-build-task) or [when a container's base image is updated](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-base-image-update).

## 3. Deploy with Azure Container Instances (ACI)

We can deploy the same application as a single stand-alone container to Azure Container Instance below. See also: [Azure Container Instances Quickstart](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-quickstart#create-a-container).

Ensure you have run the section above to set environment variables, as we are re-using these below.

```bash
# get our container registry password
CONTAINER_REGISTRY_PASSWORD=$(az acr credential show -n $CONTAINER_REGISTRY | jq -r .passwords[0].value)

# create container instance
az container create --resource-group $RESOURCE_GROUP --location $LOCATION \
    --name aci${RANDOM_STR} \
    --image "${CONTAINER_REGISTRY}.azurecr.io/${CONTAINER_IMAGE}" \
    --registry-login-server "${CONTAINER_REGISTRY}.azurecr.io" \
    --registry-username $CONTAINER_REGISTRY \
    --registry-password $CONTAINER_REGISTRY_PASSWORD \
    --cpu 1 \
    --memory 1 \
    --ports 8080 \
    --environment-variables LISTEN_PORT=8080 \
    --dns-name-label aci${RANDOM_STR}

# show container events
az container show -g $RESOURCE_GROUP -n aci${RANDOM_STR} | jq .containers[0].instanceView.events[]

# get the fully qualified domain of our container instance, set --dns-name-label above
CONTAINER_INSTANCE_FQDN=$(az container show -g $RESOURCE_GROUP -n aci${RANDOM_STR} | jq -r .ipAddress.fqdn)

# test the service in the terminal via curl
curl "${CONTAINER_INSTANCE_FQDN}:8080"

# you may also open the following URL in your web browser
echo "http://${CONTAINER_INSTANCE_FQDN}:8080"
```

# Resources 
- https://code.visualstudio.com/docs/python/tutorial-flask
- https://code.visualstudio.com/docs/python/tutorial-deploy-containers
- https://docs.microsoft.com/en-us/azure/app-service/containers/quickstart-python
- https://github.com/Microsoft/python-sample-vscode-flask-tutorial
- https://github.com/Azure-Samples/python-docs-hello-world
- https://docs.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-quick-build
- https://docs.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-build-task
- http://flask.pocoo.org/docs/1.0/quickstart/
