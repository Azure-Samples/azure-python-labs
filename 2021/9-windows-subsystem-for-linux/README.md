# Debugging a Flask App with WSL in VS Code 

## Prerequisites

You'll need the following tools installed on your local machine:

1. A machine with [Windows 10](https://www.microsoft.com/en-us/windows/get-windows-10). Alternatively, you can create a [Windows 10 Virtual Machine on Azure](https://azure.microsoft.com/en-us/pricing/details/virtual-machines/windows/).
1. The Windows Subsystem for Linux [(WSL)](https://docs.microsoft.com/en-us/windows/wsl/install-win10).
1. [Visual Studio Code](https://code.visualstudio.com/)
1. The [VS Code Remote - WSL Extension](https://aka.ms/vscode-wsl) for VS Code
1. The [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) for VS Code 
1. Ubuntu 18.04 for WSL from the [Microsoft Store](https://www.microsoft.com/en-us/p/ubuntu-1804-lts/9n9tngvndl3q?activetab=pivot:overviewtab)


## Open VS Code from WSL terminal 

1. Open a  WSL terminal window (from the start menu or by typing `wsl` from a Windows terminal). 
1. Navigate (`cd` command) to a folder where you can clone a project in.
1. Clone [this repo](https://github.com/luabud/TheCatSaidNo) by typing:
     `git clone https://github.com/luabud/TheCatSaidNo.git`
1. Navigate to the folder (`cd TheCatSaidNo`)
1. Type `code .` to open this folder in VS Code
1. Open the `app.py` file to activate the Python extension

## Install the dependencies
1. Open the terminal in VS Code (<kbd>Ctrl</kbd> + <kbd>`</kbd>)
1. Install python3-venv by typing:

   ```sudo apt-get update && sudo apt-get install python3-venv```
   
1. Create a virtual environment by typing:

    ```python3 -m venv env```

1. If a notification prompt is displayed asking if you want to select this newly created environment, click on "Yes". Otherwise, click on the Python information displayed on the status bar, located on bottom left of the screen
1.  Create a new terminal to activate the virtual environment (<kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>`</kbd>)
1. Install the dependencies:

    ``` python -m pip install -r requirements.txt```

## Run the Flask App in VS Code
1. Press <kbd>F5</kbd> to start a debug session, and select "Flask" from the configuration options.
1. <kbd>Ctrl</kbd> + Click on the link that is displayed on the terminal to access the application. 
1. Open the Debug Console in VS Code (next to the Terminal) and enter:
    ```
    import sys
    print(sys.platform)
    ``` 

## Configure and run the application tests
1. Open the command palette (<kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> or <kbd>Command</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> if you're on macOS)
1. Run the "Python: Configure Tests" command
1. Select "pytest" and then "." (root directory)
1. Click on the test beaker icon on the activity bar, on the left side. 
1. Click on the "Run All Tests" icon on the top left. 

