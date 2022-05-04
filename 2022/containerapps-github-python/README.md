# Serverless Containers with Python, Azure Container Apps, and GitHub Container Registry

In this lab you will create a sample Python app from a template repository in GitHub. You will then use the included GitHub Actions workflow which will build a container image you can then make public. You will then deploy the public container image to Azure Container Apps.

Azure Container Apps enables you to run microservices and containerized applications on a serverless platform. With Container Apps, you enjoy the benefits of running containers while leaving behind the concerns of manually configuring cloud infrastructure and complex container orchestrators.

## Requirements

- An **Azure Subscription** (e.g. [Free](https://aka.ms/azure-free-account) or [Student](https://aka.ms/azure-student-account) account)
- The [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- Bash shell (e.g. macOS, Linux, [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/about), [Multipass](https://multipass.run/), [Azure Cloud Shell](https://docs.microsoft.com/en-us/azure/cloud-shell/quickstart), [GitHub Codespaces](https://github.com/features/codespaces), etc)
- A [GitHub Account](https://github.com)

## 1. Build and Containerize asw101/python-fastapi-pypy

[Walkthrough 1/2 (vimeo.com)](https://vimeo.com/696758621/eb0fc146b4)

1. Visit <https://github.com/asw101/python-fastapi-pypy>
1. Click "Use this template".
1. Name your repo "serverless-python".
1. Create a new branch called release.
1. Click on the Actions tab.
1. View the output of the action.
1. Return to the main repo (Code tab).
1. Click on "serverless-python" under "Packages" on the right hand side.
1. Copy the `docker pull` command which will include the image name.
1. Update the `GITHUB_USER_OR_ORG` environment variable below with your GitHub username or organization name.
1. Note: If you chose to make your GitHub repository Private rather than Public in step 3, you will need to click on "Package settings" on the right hand side, scroll down and click "Change visibility" button to make your package public.

## 2. Install Azure CLI Extension and Register Resource Providers

If this is the first time you have used Azure Container Apps from the Azure CLI, or with your Azure Account, you will need to install the `containerapp` extension, and register the providers for `Microsoft.App` and `Microsoft.OperationalInsights` using the following commands.

```bash
az extension add --name containerapp

az provider register --namespace Microsoft.App --wait

az provider register --namespace Microsoft.OperationalInsights --wait
```

## 3. Set Environment Variables

[Walkthrough 2/2 (vimeo.com)](https://vimeo.com/697821473/3f706c1aca)

```bash
RESOURCE_GROUP="my-container-apps"
LOCATION="canadacentral"
CONTAINERAPPS_ENVIRONMENT="my-environment"

GITHUB_USER_OR_ORG="asw101"
CONTAINER_IMAGE="ghcr.io/${GITHUB_USER_OR_ORG}/serverless-python:release"
```

## 4. Create Resource Group

```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

## 5. Create Azure Container Apps Environment

[Quickstart (docs.microsoft.com)](https://docs.microsoft.com/en-us/azure/container-apps/get-started-existing-container-image?tabs=bash&pivots=container-apps-private-registry)

```bash
az containerapp env create \
  --name $CONTAINERAPPS_ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

## 6. Create Container App with a Public Image

```bash
az containerapp create \
  --name my-container-app \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENVIRONMENT \
  --image "$CONTAINER_IMAGE" \
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

curl "https://${CONTAINERAPP_FQDN}"
```

## 8. Delete Resource Group

```bash
az group delete \
  --name $RESOURCE_GROUP
```

## Notes

- The two video walkthroughs for section 1 and sections 2-8 based on the Go version of this lab under "Cloud Native" at <https://aka.ms/oss-labs>, but is otherwise identical.