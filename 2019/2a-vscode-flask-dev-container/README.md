# Developing a new Flask application in a Dev Container

In this lab we'll use Visual Studio Code remote development features to create a new
hello world Flask application in a dockerized development environment.

## Pre-requisites
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
1. Install [Visual Studio Code Insiders](https://code.visualstudio.com/insiders)
1. Install the [VS Code Remote Extensions](https://aka.ms/vscode-remote) 

## Create dev container
First we'll create a new dev container that we can start building our app in:
1. Open this folder using Visual Studio Code:
    ```
    cd 2a-vscode-flask-dev-container
    code-insiders .
    ```
1. Press `F1` and select `Remote-Containers: Create container configuration file...`
1. Select `Python 3` from the list
1. Select the `Reopen in Container` button in the notification that appears. If you miss the notification, 
press `F1` and select the `Remote-Containers: Re-open Folder in Container` command

After the dev container builds and installs, you will now be working in a dev container and you
can start building your app!

## Create app
Now let's create a hello world flask app. We'll need to set up the container to install flask
and expose port 8000. 
1. Take a look at the files in the workspace root:
    - `requirements.txt` defines the Python libraries to install in the dev container
    - `app.py` contains the minimal code to run a flask web server
1. Open `.devcontainer/.devcontainer.json` and expose port 5000 by adding ```"appPort": 5000```. The .json file should look as follows:
    ```
    {
        "name": "Python 3",
        "context": "..",
        "dockerFile": "Dockerfile",
        "workspaceFolder": "/workspace",
        "extensions": [
            "ms-python.python"
        ],
        "appPort": 5000
    }
    ```
    NOTE: Don't forget to press Ctrl-S to save!

1. Now let's rebuild the container so that it installs flask via the requirements.txt file and
exposes port 5000. Press `F1` and select `Remote-Containers: Rebuild container`. 
1. Add a debug configuration, `Debug > Add Configuration`. Select `Flask`.
1. Edit the `launch.json` file generated to have the app bind to host `0.0.0.0` by adding host to args as follows:
    ```
    "args": [
        "run",
        "--host","0.0.0.0",
        "--no-debugger",
        "--no-reload"
    ],
    ```
1. Press `F5` to start debugging, browse to your app at [http://localhost:5000](http://localhost:5000).
1. Optionally set a breakpoint on line 6 of the app and refresh the page
