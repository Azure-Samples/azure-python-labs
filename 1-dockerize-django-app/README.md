# Containerize a Django application using Visual Studio Code

Let's start with a simple Django web application that allows you to log messages and saves them 
to a SQLite database.

We'll take this application and use Visual Studio Code to package the application
up in a docker container.

## Pre-requisites
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
1. Install [Visual Studio Code](https://code.visualstudio.com)
1. Install the [VS Code Docker Extension](https://marketplace.visualstudio.com/items?itemName=PeterJausovec.vscode-docker)

## Open workspace and build a development container
1. Open this folder using Visual Studio Code:
    ```
    cd 1-dockerize-django-app
    code .
    ```
1. Run `Ctrl-Shift-P` and type `Add Docker files to Workspace`
1. Following the prompts select `Python` and ports `8000`
1. Change the RUN and CMD lines to the following:
    ```Dockerfile
    # Using pip:
    RUN python3 -m pip install -r requirements.txt
    RUN python3 manage.py migrate
    CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
    ```
1. Right-click on docker-compose.yml and click compose up
1. Open [http://localhost:8000](http://localhost:8000) in the browser to view the app

## Build a production-ready container
Now let's update the image to use a production webserver using nginx and uwsgi. 
The application already contains a uwsgi.ini file which defines how to run the web server,
so we just need to make some small modifications to our Dockerfile.

1. Remove the CMD line from the Dockerfile.
1. Change the FROM line to:
    ```Dockerfile
    FROM tiangolo/uwsgi-nginx
    ```
1. Replace the EXPOSE line with
    ```Dockerfile
    ENV LISTEN_PORT=8000
    ```
1. Right-click on docker-compose.yml and click compose up
1. Open [http://localhost:8000](http://localhost:8000) in the browser to view the app



