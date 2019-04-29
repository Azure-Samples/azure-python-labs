# Azure Python Labs

A collection of labs demonstrating how to build Python applications with Azure and Visual Studio Code.

## Containerize a Django application using Visual Studio Code

...

[Go to lab](1-vscode-django-docker/README.md)

## Developing a Django+PostgreSQL application in a Dev Container

...

[Go to lab](2-vscode-django-postgres-dev-container/README.md)

## Python Primacy on Azure Functions

...

[Go to lab](4-azure-functions-python/README.md)

## Detecting Emotion with Azure Cognitive Services

...

[Go to lab](5-jupyter-azure-cognitive-services-face/README.md)

## Build a Movie Recommendation system using Azure Machine Learning

This tutorial will walk through how to build a Movie Recommender system trained with a Simple Algorithm for Recommenders (SAR) for the Movielens dataset on Azure Machine Learning service. It demonstrates how to use the power of the cloud to manage data, switch to powerful GPU machines, and monitor runs while training a model. In this lab you will:

- Connect to an Azure Machine Learning service workspace
- Access movielens data from a datastore
- Connect to cpu and gpu machines from Azure Machine Learning Compute
- Create a training script using the recommender repo's util functions for SAR and add logging information
- Submit the training job to AzureML, and monitor the run with a jupyter widget
- Test an existing model with new user data
- **Optional Part 2**: Deploy the model to a web service using Azure Container Instance.

[Go to lab](6-azureml-movie-recommendation/README.md)

## Application messaging with Azure Service Bus

...

[Go to lab](8-azure-service-bus-messaging/README.md)

## Containerize and Deploy a Python Flask application with Azure Container Registry and Azure Container Instances

In this lab you will learn to:
1. Build a Python Flask application using Docker and a Dockerfile.
2. Build the container image in the cloud using Azure Container Registry (ACR).
3. Deploy the container image to Azure Container Instances (ACI).

[Go to lab](3-azure-cli-flask-registry-container-instances/README.md) | Duration: 5-10 minutes

## Configure continuous integration builds for a Python project hosted in GitHub

In this lab you will learn to:
1. Set up Azure Pipelines to build and test a Python project hosted in GitHub.
2. Customize the build by configuring the YAML build definition.
3. Validate pull requests using GitHub Checks and Azure Pipelines

[Go to lab](7-azure-pipelines-ci/README.md) | Duration: 5 minutes
