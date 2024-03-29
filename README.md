---
page_type: sample
languages:
- python
products:
- azure
description: "A collection of labs demonstrating how to build Python applications with Azure and Visual Studio Code."
urlFragment: azure-python-labs
---

# Azure Python Labs

A collection of labs demonstrating how to build Python applications with Azure and Visual Studio Code.

Join the Microsoft Python Discord (http://aka.ms/python-discord ) and the **#python-virtual-labs** channel to ask questions, get help with labs, and/or further instructions (also see: <https://aka.ms/python-virtual-labs> for our PyCon 2022 experience).

## Python & Visual Studio Code in the browser with vscode.dev

[vscode.dev](https://vscode.dev/) is a lightweight version of [Visual Studio Code](https://code.visualstudio.com/) that runs fully in the browser, providing the ability to navigate files and repositories, and it's ideal for committing lightweight code changes.

In this lab, we will go through the process of creating and running Python code in Jupyter Notebooks on the browser. We'll create a simplified version of the popular [wordle](https://www.nytimes.com/games/wordle/index.html) game.

[Python & Visual Studio Code in the browser with vscode.dev](2022/python-vscode-dev/README.md)

## Cloud Native Python with Azure Container Apps, Azure Container Registry, and FastAPI on PyPy

In this lab you will containerize an existing Python application using the Azure CLI, a private Azure Container Registry, and Azure Container Registry Tasks. You will then deploy it to Azure Container Apps, which enables you to run microservices and containerized applications on a serverless platform.

[Cloud Native Python with Azure Container Apps, Container Registry, and FastAPI on PyPy](2022/containerapps-python-fastapi/README.md)

## Serverless Containers with Python, Azure Container Apps, and GitHub Container Registry

In this lab you will create a sample Python app from a template repository in GitHub. You will then use the included GitHub Actions workflow which will build a container image you can then make public. You will then deploy the public container image to Azure Container Apps, which enables you to run microservices and containerized applications on a serverless platform.

[Serverless Containers with Python, Azure Container Apps, and GitHub Container Registry](2022/containerapps-github-python/README.md)

## Sentiment Analysis with Python Azure Functions

In this lab, you will build a serverless HTTP API with Azure Functions that takes a sentence as an input and returns the sentiment of the sentence.

- Build a serverless HTTP API with Azure Functions
- Run and debug the API locally on your machine
- Deploy the API to Azure Functions

[Sentiment Analysis with Python Azure Functions lab](01-azure-functions-python-vscode/README.md)

## Cyber Security Investigations and Analysis with MSTICPy

This lab is an introduction to MSTICPy - an open source cyber security tool kit created by the Microsoft Threat Intelligence Center. In this lab you will learn about the core features of MSTICPy, and how to use to them in cyber security incident response or threat hunting. This lab takes the form of a Jupyter Notebook that you can run locally or directly in your browser.

[Cyber Security Investigations and Analysis with MSTICPy lab](01-msticpy/README.md)


## Explore Azure Database for PostgreSQL with Python

In this lab, you will learn how to import data into an Azure Database for PostgreSQL instance using a python script and the `psycopg2` module. You will learn to:

- Connect to an Azure Database for PostgreSQL
- Use the `psycopg2` to load and query data in the database.

[Azure Databse for PostgreSQL with Python lab](01-postgres/README.md)


## Explore the Distributed Application Runtime (Dapr) with Python

- Get hands-on with Dapr by running it on your local machine through the [Try Dapr](https://docs.dapr.io/getting-started/) experience.
- Explore State Mangement and Secrets building blocks via the REST API using cURL (optional), Python Requests, and the Dapr SDK for Python ([dapr/python-sdk](https://github.com/dapr/python-sdk)).
- Seamlessly swap the State component from local development to a managed service in the cloud.

[Explore the Distributed Application Runtime (Dapr) with Python lab](01-dapr/README.md)


## Real-Time Analytics on Azure Database for PostgreSQL - Hyperscale (Citus)

This workshop is meant to be an introduction to Azure Database for PostgreSQL Hyperscale (Citus). First, you will create a cluster to scale out PostgreSQL and turn it into a distributed database. Then, you will create a schema and tables, load test data, and create a rollup function to massively speed up your query workload.

[Real-Time Analytics on Azure Database for PostgreSQL lab](01-postgres-citus/README.md)

---

## [2021](2021/README.md) | [2020](2020/README.md) | [2019](2019/README.md)
