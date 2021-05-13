# Azure Python Labs (2019) [[back](../)]

## Containerize a Django application using Visual Studio Code

Build a docker container to run a Django app using the Docker extension in Visual Studio Code to generate Dockerfiles and run the containers.

[Containerize a Django application using Visual Studio Code lab](1-vscode-django-docker/README.md)

## Developing a new Flask application in a Dev Container

Build a new dev container using Visual Studio Code remote from scratch and create a simple Flask app inside of the new environment.

[Developing a new Flask application in a Dev Container lab](2a-vscode-flask-dev-container/README.md)

## Developing a Django+PostgreSQL application in a Dev Container

Open an existing dev container using Visual Studio Code remote extensions, build a React front-end, initialize a PostgreSQL database, and run a Django app. 

[Developing a Django+PostgreSQL application in a Dev Container lab](2b-vscode-django-postgres-dev-container/README.md)

## Use Azure Functions to Find Primes

Create an Azure Function in Python with an HTTP endpoint that will respond with whether or not your input is a prime number.

- Create an Azure Function using the command line interface.
- Test the default "Hello, World" Function.
- Edit the code run when the endpoint is called to determine if an input is prime.
- Test the new functionality with your own inputs.

[Use Azure Functions to Find Primes lab](4-azure-functions-python/README.md)

## Detecting Emotion with Azure Cognitive Services

Use a Jupyter Notebook and Azure Cognitive Services to analyze images in real time to detect faces and their dominant emotions.

In this lab you will:

- Connect to Azure Cognitive Services (ACS).
- Test the raw response from ACS.
- Use this response to create an overlay plotting the detected faces and emotions over any given image.
- Test it out with any image you want!

[Detecting Emotion with Azure Cognitive Services lab](5-jupyter-azure-cognitive-services-face/README.md)

## Build a Movie Recommendation system using Azure Machine Learning

Build a Movie Recommender system trained with a Simple Algorithm for Recommenders (SAR) for the Movielens dataset on Azure Machine Learning service. Use the power of the cloud to manage data, switch to powerful GPU machines, and monitor runs while training a model. 

In this lab you will:

- Connect to an Azure Machine Learning service workspace
- Access Movielens data from a datastore
- Connect to CPU and GPU machines from Azure Machine Learning Compute
- Create a training script using the recommender repo's util functions for SAR and add logging information
- Submit the training job to AzureML, and monitor the run with a Jupyter widget
- Test an existing model with new user data
- **Optional Part 2**: Deploy the model to a web service using Azure Container Instance.

[Build a Movie Recommendation system using Azure Machine Learning lab](6-azureml-movie-recommendation/README.md)

## Application messaging with Azure Service Bus

This tutorial walks you through building a messaging system on Azure Service Bus that allows you to pass information back and forth between unconnected programs,
with a small Flask application that has two messaging endpoints: One for sending messages to a queue, and one for retrieving them. Service Bus messaging can
be used by applications which aren't connected to or authenticated with Azure, as long as they have the authentication tokens for the messaging system itself.

In this lab you will:

1. Create Service Bus resources on Azure.
2. Program a small Flask application to run locally.
3. Send and receive messages without signing in to an Azure account.
4. **Optional** Experiment with other ways to process queued messages.

[Application messaging with Azure Service Bus lab](8-azure-service-bus-messaging/README.md) | Duration: 10-15 minutes

## Containerize and Deploy a Python Flask application with Azure Container Registry and Azure Container Instances

In this lab you will learn to:
1. Build a Python Flask application using Docker and a Dockerfile.
2. Build the container image in the cloud using Azure Container Registry (ACR).
3. Deploy the container image to Azure Container Instances (ACI).

[Containerize and Deploy a Python Flask application with Azure Container Registry and Azure Container Instances lab](3-azure-cli-flask-registry-container-instances/README.md) | Duration: 5-10 minutes

## Configure continuous integration builds for a Python project hosted in GitHub

In this lab you will learn to:
1. Set up Azure Pipelines to build and test a Python project hosted in GitHub.
2. Customize the build by configuring the YAML build definition.
3. Validate pull requests using GitHub Checks and Azure Pipelines

[Configure continuous integration builds for a Python project hosted in GitHub lab](7-azure-pipelines-ci/README.md) | Duration: 5 minutes
