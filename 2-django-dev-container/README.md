# Developing a Django+PostgreSQL application in a Dev Container

In this lab we'll use Visual Studio Code remote development features to work on a 
a Django+PostgreSQL application in a dockerized development environment.

## Open the dev container workspace
1. Clone the sample app and open using Visual Studio Code:
    ```
    git clone https://github.com/Microsoft/python-sample-tweeterapp
    cd python-sample-tweeterapp
    code-insiders .
    ```
1. Click the ```Reopen in Container``` prompt, or press `Ctrl-Shift-P` and select the `Re-open folder in dev container` command
1. After the container builds, open the terminal using ```Ctrl-` ``` and type
    ```
    python manage.py migrate
    python manage.py loaddata initial_data
    python manage.py runserver
    ```
1. Open [http://localhost:5000](http://localhost:5000) in the browser to view the app

## Set up debugging in the container
1. From the `Debug` menu, select `Start Debugging`
1. Following the prompts select Django, and port 5000
1. Open `tweeter/views.py`, set a breakpoint on line 13
1. Refresh the app in the browser to hit the breakpoint
1. Open the debug console `Views > Debug Console`, and type `bob` into the debug console to inspect the user


