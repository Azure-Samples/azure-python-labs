# Cloud Native Python with Azure Container Apps, Azure Container Registry, and FastAPI on PyPy

[Walkthrough (vimeo.com)](https://vimeo.com/695948817/572d6bbbcd)

In this lab you will containerize an existing Python application using the Azure CLI, a private Azure Container Registry, and Azure Container Registry Tasks. You will then deploy it to Azure Container Apps.

Azure Container Apps enables you to run microservices and containerized applications on a serverless platform. With Container Apps, you enjoy the benefits of running containers while leaving behind the concerns of manually configuring cloud infrastructure and complex container orchestrators.

## Requirements

- An **Azure Subscription** (e.g. [Free](https://aka.ms/azure-free-account) or [Student](https://aka.ms/azure-student-account) account)
- The [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- Bash shell (e.g. macOS, Linux, [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/about), [Multipass](https://multipass.run/), [Azure Cloud Shell](https://docs.microsoft.com/en-us/azure/cloud-shell/quickstart), [GitHub Codespaces](https://github.com/features/codespaces), etc)

## 1. Clone Sample

```bash
git clone https://github.com/asw101/python-fastapi-pypy.git

cd python-fastapi-pypy/
```

## 2. Set Environment Variables

```bash
RESOURCE_GROUP="my-container-apps"
LOCATION="canadacentral"
CONTAINERAPPS_ENVIRONMENT="my-environment"

SUBSCRIPTION_ID=$(az account show --query id --out tsv)
SCOPE="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}"
[[ -z "${RANDOM_STR:-}" ]] && RANDOM_STR=$(echo -n "$SCOPE" | shasum | head -c 6)

ACR_NAME="acr${RANDOM_STR}"
ACR_IMAGE_NAME="pypy-fastapi:latest"
```

## 3. Create Resource Group

```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

## 4. Create Azure Container Registry

[Quickstart (docs.microsoft.com)](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-azure-cli)

```bash
az acr create --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

az acr build -t $ACR_IMAGE_NAME -r $ACR_NAME .

CONTAINER_IMAGE="${ACR_NAME}.azurecr.io/${ACR_IMAGE_NAME}"
REGISTRY_SERVER="${ACR_NAME}.azurecr.io"
REGISTRY_USERNAME="${ACR_NAME}"
REGISTRY_PASSWORD=$(az acr credential show -n $ACR_NAME --query 'passwords[0].value' --out tsv)

echo "$CONTAINER_IMAGE"
```

## 5. Create Azure Container Apps Environment

[Quickstart (docs.microsoft.com)](https://docs.microsoft.com/en-us/azure/container-apps/get-started-existing-container-image?tabs=bash&pivots=container-apps-private-registry)

```bash
az extension add --name containerapp

az containerapp env create \
  --name $CONTAINERAPPS_ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

## 6. Create Container App

```bash
az containerapp create \
  --name my-container-app \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENVIRONMENT \
  --image "$CONTAINER_IMAGE" \
  --registry-server "$REGISTRY_SERVER" \
  --registry-username "$REGISTRY_USERNAME" \
  --registry-password "$REGISTRY_PASSWORD" \
  --target-port 80 \
  --ingress 'external'
```

## 7. Test Container App with curl

```bash
CONTAINERAPP_FQDN=$(az containerapp show --resource-group $RESOURCE_GROUP \
  --name my-container-app \
  --query properties.configuration.ingress.fqdn \
  --out tsv)

echo "https://${CONTAINERAPP_FQDN}"

curl "https://${CONTAINERAPP_FQDN}/"
```

## 8. Delete Resource Group

```bash
az group delete \
  --name $RESOURCE_GROUP
```

## Notes

- The sample in section 1 is originally from <https://github.com/tonybaloney/ants-azure-demos>, which is also referenced in step 1 of the video walkthrough. The updated sample is at: <https://github.com/asw101/python-fastapi-pypy>.
