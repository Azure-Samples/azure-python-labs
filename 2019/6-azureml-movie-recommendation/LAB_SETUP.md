# Lab Setup

## Prerequisites

- **Azure Subscription**: If you don’t have an Azure subscription, create a free account before you begin. Try the [free or paid version of Azure Machine Learning service today](https://azure.microsoft.com/en-us/free/services/machine-learning/).
- **Azure Machine Learning Service Workspace**: You will need an AzureML service workspace to run this lab at home.

> With a new account, you get credits to spend on Azure services, which will easily cover the cost of running this example notebook. After they're used up, you can keep the account and use [free Azure services](https://azure.microsoft.com/en-us/free/). Your credit card is never charged unless you explicitly change your settings and ask to be charged. Or [activate MSDN subscriber benefits](https://azure.microsoft.com/en-us/pricing/member-offers/credit-for-visual-studio-subscribers/), which give you credits every month that you can use for paid Azure services.

## Set Up an Azure Machine Learning Service Workspace

From the Azure Portal, select the `+` symbol in the left bar to add a new resource. In the blade that appears, type `Machine Learning service workspace` into the search bar. Press `Enter` and click the `Create` button on the blade that appears. You will be prompted to set the following values: `Workspace name`, `Subscription`, `Resource group`, and `Location`. After setting them how you like, click the `Create` button and Azure will begin to deploy your resource. 

Go to the resource once it is deployed. On the resource blade, click `Download config.json` and copy the file to the same directory in which this file is located. You may be replacing an existing `config.json`.

