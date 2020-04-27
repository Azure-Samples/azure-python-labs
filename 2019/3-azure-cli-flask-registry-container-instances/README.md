# Containerize and Deploy a Python Flask application with Azure Container Registry and Azure Container Instances

In this lab you will learn to:
- Build a Python Flask application using Docker and a Dockerfile.
- Build the container image in the cloud using Azure Container Registry (ACR).
- Deploy the container image to Azure Container Instances (ACI).

## 1. Explore Docker and Dockerfiles

If you have Docker installed locally, you have three options to build and run the Flask application inside a container.

> __IMPORTANT__: This section is **for illustrative purposes only** and you **do not** need to run these commands. 

Clone the Visual Studio Code Flask tutorial:

```bash
git clone https://github.com/Microsoft/python-sample-vscode-flask-tutorial
cd python-sample-vscode-flask-tutorial/
```

Run the application from inside of a Docker container: 

```bash
docker run --rm -v ${PWD}:/pwd/ -w /pwd/ -p 8080:5000 -it python bash
pip install -r requirements.txt
export FLASK_APP=startup.py
flask run --host=0.0.0.0
# open http://localhost:8080
```

Build a *development* container from a `Dockerfile` ([dev.Dockerfile](dev.Dockerfile)).

```bash
docker build -f dev.Dockerfile -t test python-sample-vscode-flask-tutorial/
docker run --rm -p 8080:5000 -it test
# open http://localhost:8080
```

Build a *production* container from a `Dockerfile` ([prod.Dockerfile](prod.Dockerfile)).
```bash
docker build -f prod.Dockerfile -t prod python-sample-vscode-flask-tutorial/
docker run --rm -p 8080:5000 -it prod
# open http://localhost:8080
```

## 2. Build with Azure Container Registry (ACR)

Azure Container Registry is Azure's private container registry. It has the ability to build a container image inside the registry from source code and a Dockerfile.

The snippet below the correct value for the `RESOURCE_GROUP` variable. This can be set manually as below, or via the `az group list` command with `jq` to select the name of the "first group that starts with Group-". If you're doing this lab on your own, **not at an event**, you will need to un-comment and **set the RESOURCE_GROUP variable manually**.

The Azure Container Registry's name must also be globally unique, so here `CONTAINER_REGISTRY` to `acr` with a 6 character random suffix.

First set some environment variables:

```bash
# RESOURCE_GROUP='Group-...'
RESOURCE_GROUP=$(az group list | jq -r '[.[].name|select(. | startswith("Group-"))][0]')
LOCATION='centralus'
if [ -z "$RANDOM_STR" ]; then RANDOM_STR=$(openssl rand -hex 3); else echo $RANDOM_STR; fi
# RANDOM_STR='9c445c'
CONTAINER_REGISTRY=acr${RANDOM_STR}
CONTAINER_IMAGE='hello-flask:latest'
```

If you are not yet logged in:

```bash
az login
```

Create the resource group, if required:

```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
```

Now use the Azure CLI (az) to create an Azure Container Registry and build an image in the cloud.

```bash
az acr create -g $RESOURCE_GROUP -l $LOCATION --name $CONTAINER_REGISTRY --sku Basic --admin-enabled true
```

Clone the source code from our sample repository:

```bash
git clone https://github.com/Microsoft/python-sample-vscode-flask-tutorial
```

Next run the [az acr build](https://docs.microsoft.com/en-us/cli/azure/acr?#az-acr-build) command, which will push the source code and Dockerfile to the cloud, build the image, and store it in the Azure Container Registry:

```bash
az acr build -r $CONTAINER_REGISTRY -t hello-flask --file prod.Dockerfile python-sample-vscode-flask-tutorial/
```

The fully-qualified name of the image in your Container Registry is `$CONTAINER_REGISTRY'.azurecr.io/hello-flask:latest'`. Output this with:

```bash
echo "${CONTAINER_REGISTRY}.azurecr.io/hello-flask:latest"
```

Now you've published your first image on Azure Container Registry. You can run this image in any environment with Docker with the commands:

```bash
az acr login -n $CONTAINER_REGISTRY
docker run -it $CONTAINER_REGISTRY'.azurecr.io/hello-flask:latest'
```

Since Azure Container Registry (ACR) is completely private, you need to log in with `az acr login` in order to use the image built inside the registry. 

Images hosted on public container registries, such as Docker Hub, can be accessed without authentication. This image is also available on Docker Hub at: `aaronmsft/hello-flask`

In addition to the ACR Tasks [quick task](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-quick-task) feature explored above, Azure Container Registry enables you to automatically trigger image builds in the cloud [when you commit source code to a Git repository](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-build-task) or [when a container's base image is updated](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-base-image-update).

## 3. Deploy with Azure Container Instances (ACI)

You can deploy the same application as a single stand-alone container to Azure Container Instances with the [az container create](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-quickstart#create-a-container) command.

Ensure you have run the section above to set environment variables, as these are re-used:

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
- https://docs.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-quick-task
- https://docs.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-build-task
- https://docs.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-base-image-update
- https://docs.microsoft.com/en-us/azure/container-instances/container-instances-quickstart
- https://docs.microsoft.com/en-us/azure/app-service/containers/quickstart-python
- https://code.visualstudio.com/docs/python/tutorial-flask
- https://code.visualstudio.com/docs/python/tutorial-deploy-containers
- https://github.com/Microsoft/python-sample-vscode-flask-tutorial
- https://github.com/Azure-Samples/python-docs-hello-world
- http://flask.pocoo.org/docs/1.0/quickstart/
