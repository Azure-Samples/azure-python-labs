# Number Facts with Python Web Apps

In this lab, you will learn how to deploy a python app to App Service using the Azure CLI.

You will learn to:

- Use  `az webapp up` to quickly provision Azure resources and deploy your app to Azure App Service.
- Leverage the `local context` feature of Azure CLI to ease management operations.

## Prerequisites

- macOS, Windows, or Linux
- Azure Subscription
- [Python](https://www.python.org/downloads/) 3.7, or 3.8
- [Git](https://git-scm.com/)
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest)

## Deploy the app to Azure using the Azure CLI

### Create a local copy of this repository
  
- You can create a local clone, or just download the *.zip archive
- Open a terminal window and navigate to the folder containing the Web App sample

### Login with Azure CLI

Log in to Azure using the `az login` command. This will open a browser window where you can authenticate.  [See az login](https://docs.microsoft.com/cli/azure/reference-index?view=azure-cli-latest#az-login).

Choose the subscription you will use with the `az account set --subscription` command. You will only need to do this if you have more than one Azure subscription.
[See az account](https://docs.microsoft.com/cli/azure/account?view=azure-cli-latest#az-account-set).

### Deploy your application with az webapp up

App Service provides `az webapp up` as a quick way to get started with the service. We are going to leverage that functionality to:

- Create all the necessary resources to host our app
- Build and package the application
- Publish the app to the cloud.

Run the following command:

``` bash
  az webapp up -n <name> -l <location> -sku FREE
```

- **name** should be a unique string. **name** is used as the Azure resource name as well as part of the url for your app.

- **location** will determine the Azure region where your resource will be created. You can get a list of supported locations with `az account list-locations`.

- **sku** lets you choose across different service offerings. For this sample we will use the FREE option, however for production we recommend `P1V2` or higher. [Learn more about App Service Pricing](https://azure.microsoft.com/pricing/details/app-service/windows/)

> Note: App Service has limits on how many free plans you can have in a subscription. If you have problems creating a free plan, try choosing a different region, or using one of the paid options such as B1.

Running `az webapp up` for the first time will take a few minutes to complete. Behind the scenes it will provision all the necessary resources including an [Azure Resource Group](https://docs.microsoft.com/azure/azure-resource-manager/management/overview#resource-groups), [App Service plan](https://docs.microsoft.com/azure/app-service/overview-hosting-plans) and [Azure Webapp](https://docs.microsoft.com/azure/app-service/containers/app-service-linux-intro).

Locally `az webapp up` creates a directory called `.azure` this is used to store the *local context*. Local context stores the configuration that you passed in through parameters to `az webapp up` to use later. For example you can now use `az webapp browse` without any more parameters to browse to your app or `az webapp logs tail` to stream the runtime logs of your application.

You can also modify this sample and run `az webapp up` again with no parameters to push any change you have made to the resources you already created on the first run.

[Learn more about az webapp up](https://docs.microsoft.com/cli/azure/webapp?view=azure-cli-latest#az-webapp-up)
