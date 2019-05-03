# Containerize a Django application using Visual Studio Code

This lab teaches you how to use Visual Studio Code's Docker extension to build a Docker container for an existing Django web application which
takes log messages and stores them in an SQLite database.

The container that you use in this lab will be used in other labs that teach you how to publish a Docker container.

## Prerequisites

If you're doing this lab outside of the Microsoft booth at PyCon 2019, you'll need the following tools installed on your local machine:

1. [Docker Desktop](https://www.docker.com/products/docker-desktop)
1. [Visual Studio Code](https://code.visualstudio.com)
1. The [VS Code Docker Extension](https://marketplace.visualstudio.com/items?itemName=PeterJausovec.vscode-docker)

## Open workspace and build a development container

1. Open the lab folder with Visual Studio Code:

    ```bash
    cd 1-vscode-django-docker
    code-insiders .
    ```

1. Run `Ctrl-Shift-P` and type `Add Docker files to Workspace`.
1. Following the prompts select `Python` and port `8000`.
1. Change the RUN and CMD lines in the Dockerfile to the following:

    ```Dockerfile
    # Using pip:
    RUN python3 -m pip install -r requirements.txt
    RUN python3 manage.py migrate
    CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
    ```

1. Right-click on docker-compose.yml and click `Compose up`.
1. Open [http://localhost:8000](http://localhost:8000) in the browser to view the app.

## (Optional) Build a production-ready container

If you want to build a container using a production webserver using nginx and uwsgi, you can follow the steps below.

The application already contains a `uwsgi.ini` file which defines how to run the web server,
so you only need to make some small modifications to the Dockerfile.

1. Remove the CMD line from the Dockerfile.
1. Change the FROM line to:

    ```Dockerfile
    FROM tiangolo/uwsgi-nginx
    ```

1. Replace the EXPOSE line with

    ```Dockerfile
    ENV LISTEN_PORT=8000
    ```

1. Right-click on docker-compose.yml and click `Compose up`.
1. Open [http://localhost:8000](http://localhost:8000) in the browser to view the app.
