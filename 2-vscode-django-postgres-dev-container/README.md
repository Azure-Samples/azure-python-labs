# Developing a Django+PostgreSQL application in a Dev Container

In this lab we'll use Visual Studio Code remote development features to work on a 
Django+PostgreSQL application in a dockerized development environment.

## Pre-requisites
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
1. Install [Visual Studio Code Insiders](https://code.visualstudio.com/insiders)
1. Install the [VS Code Remote Extensions](https://aka.ms/vscode-remote) 

## Open the dev container workspace
1. Clone the sample app and open using Visual Studio Code:
    ```
    git clone https://github.com/Microsoft/python-sample-tweeterapp
    cd python-sample-tweeterapp
    code-insiders .
    ```
1. Click the ```Reopen in Container``` prompt, or press `Ctrl-Shift-P` and select the `Re-open folder in dev container` command
1. After the container builds, open a new terminal using ```Ctrl-Shift-` ``` and type
    ```
    python manage.py migrate
    python manage.py loaddata initial_data
    python manage.py runserver
    ```
1. Open [http://localhost:8000](http://localhost:8000) in the browser to view the app

## Set up debugging in the container
1. From the `Debug` menu, select `Start Debugging`
1. Select the `Django` debug configuration from the menu
1. Open `tweeter/views.py`, set a breakpoint on line 14
1. Refresh the app in the browser to hit the breakpoint
1. Open the debug console `Views > Debug Console`, and type `bob` into the debug console to inspect the user
1. Look up the user's e-mail address by inspecting the variable in the debug console


