# Developing a Django+PostgreSQL application in a Dev Container

In this lab you use Visual Studio Code remote development features to work on a Django+PostgreSQL application in a dockerized development environment.

> __IMPORTANT__: Right now, you cannot use WSL as your shell to either open Visual Studio Code or as your default shell inside
> of Visual Studio Code and also use the VS Code Remote Extensions. To change the shell, press `Ctrl-Shift-P` and select
> `Terminal: Select Default Shell`. When prompted for a value, choose either `CMD` or `PowerShell`. Close any existing shells,
> and a new one will open with the selected default.

## Prerequisites

If you're doing this lab outside of the Microsoft booth at PyCon 2019, you'll need the following tools installed on your local machine:

1. [Docker Desktop](https://www.docker.com/products/docker-desktop)
1. [Visual Studio Code Insider Build](https://code.visualstudio.com/insiders)
1. The [VS Code Remote Extensions](https://aka.ms/vscode-remote) 
1. If you are running on windows, set your git line endings to use LF:
    ```
    git config --global core.autocrlf false
    ```

## Open the dev container workspace

1. Clone the sample app and open using Visual Studio Code:

    ```cmd
    git clone https://github.com/Microsoft/python-sample-tweeterapp
    cd python-sample-tweeterapp
    code-insiders .
    ```

1. Click the `Reopen in Container` prompt, or press `F1` and select the `Reopen folder in dev container` command.

1. After the workspace terminal loads, open a new terminal using ```Ctrl-Shift-` ``` and type the following to build the React frontend:

    ```cmd
    npm install
    npm run dev
    ```

1. After the container builds, open another terminal using ```Ctrl-Shift-` ``` and type:

    ```cmd
    python manage.py migrate
    python manage.py loaddata initial_data
    python manage.py runserver
    ```

1. Open [http://localhost:8000](http://localhost:8000) in the browser to view the app.
1. Create an account and login to the app

## Set up debugging in the container

1. Stop the app in the terminal by pressing `Ctrl-C` (otherwise the port will be taken when you debug)
1. From the `Debug` menu, select `Start Debugging`.
1. Select the `Django` debug configuration from the menu.
1. Open `tweeter/views.py`, set a breakpoint on line 26
1. Refresh the app in the browser to hit the breakpoint
1. Open the debug console `Views > Debug Console`, and type `request.user` into the debug console to inspect the logged in user
