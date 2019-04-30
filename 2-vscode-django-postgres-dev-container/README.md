# Developing a Django+PostgreSQL application in a Dev Container

In this lab we'll use Visual Studio Code remote development features to work on a Django + PostgreSQL application in a dockerized development environment.

## Pre-requisites
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
1. Install [Visual Studio Code Insiders](https://code.visualstudio.com/insiders)
1. Install the [VS Code Remote Extensions](https://aka.ms/vscode-remote) 

## Open the dev container workspace
1. Clone the sample app and open using Visual Studio Code:

    ```bash
    git clone https://github.com/Microsoft/python-sample-tweeterapp
    cd python-sample-tweeterapp
    code-insiders .
    ```

1. Click the ```Reopen in Container``` prompt, or press `F1` and select the `Reopen folder in dev container` command

1. After the workspace terminal loads, open a new terminal using ```Ctrl-Shift-` ``` and type the following to build the React frontend:

    ```bash
    npm install
    npm run dev
    ```

1. Open another using ```Ctrl-Shift-` ``` and type the following to initialize the database and run the Python backend:

    ```bash
    python manage.py migrate
    python manage.py loaddata initial_data
    python manage.py runserver
    ```

1. Open [http://localhost:8000](http://localhost:8000) in the browser to view the app
1. Create an account and login to the app

## Set up debugging in the container
1. From the `Debug` menu, select `Start Debugging`
1. Select the `Django` debug configuration from the menu
1. Open `tweeter/views.py`, set a breakpoint on line 26
1. Refresh the app in the browser to hit the breakpoint
1. Open the debug console `Views > Debug Console`, and type `request.user` into the debug console to inspect the logged in user


