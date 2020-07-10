# Hello World in Visual Studio Codespaces

In this lab you will create a hello world script in Visual Studio Codespaces to experiment with the development experience on the browser.

## Prerequisites

You'll need the following tools installed on your local machine:

1. A [supported browser](https://docs.microsoft.com/en-us/visualstudio/online/resources/troubleshooting#partially-supported-browsers)
1. Azure Credentials.

## Create a Codespace
1. Navigate to https://aka.ms/vscodespaces, click on the "Sign in" button and enter your Azure credentials. 
1. Click on the "Create Codespace" button, and add "HelloWorld" to the `Codespace Name` field.
1. Add https://github.com/asw101/hello-vscodespaces to the `Git repository` field. This repo contains a simple Hello World Flask application. 
1. Click on the "Create" button. You can leave the other fields with the default values. 

## Create a Hello World script
1. Open the Command Palette (<kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd>, or <kbd>Command</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> if you're on macOS) and run the `File: New File` command.
1. Name it `hello.py`, and open it on VS Codespaces.
1. Add `print("Hello, VS Codespaces!")` to the file and save it (<kbd>Ctrl</kbd> + <kbd>S</kbd>).
1. Right click on the editor select `Run Python File in Terminal`. This will run your hello world script in the terminal.

## Debug the Hello World Flask app

1. Check that VS Codespaces created a virtual environment called `pythonenv3.7` located on the top of the project.
1. Make sure this environment is selected by clicking on the Python environment information on the status bar, localted on the bottom left of the screen. 
1. Start a debug session :

    - Open the Run/Debug view by clicking on the play + bug icon on the activity bar, on the left side of the screen. Then click on the "Run and Debug" button.

    - Or press <kbd>F5</kbd>
1. From the configuration drop-down, select "Flask"
1. You should see the following message on the terminal: 
```
 * Serving Flask app "app.py"
 * Environment: development
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 ```
 6. Press <kbd>Ctrl</kbd> and click on the link on the terminal to access the application on a new tab. 


## Additional things to try
1. **Edit:**
   - Open `app.py`
   - Try adding some code and check out the language features.
   
1. **Try out Flask live reloading while debugging:**
   
   - Create a configuration file for the debugger by opening the Run/Debug view and clicking on "create a launch.json file"
   - Select Flask from the configuration options
   - Delete lines 19 and 20 ("--no-debugger" and "--no-reload")
   - Change "FLASK_DEBUG" on line 15 to "1". 
   - Press <kbd>F5</kbd> to start the debug session using that new configuration
   - Open the `app.py` file, make a change and save it.  
1.  **Add a logpoint**:
   
    - Open `app.py` and right click on the left side of line 5
    - Select `Add logpoint...` 
    - Enter "Executing endpoint" and hit <kbd>Enter</kbd>
    - Press F5 to run the Flask app and <kbd>Ctrl</kbd> + Click on the link to open it on a new tab
    - Open the Debug Console panel (next to the terminal) and see the logged message.


## Other samples
- [Tweeter App - Python and Django](https://github.com/Microsoft/python-sample-tweeterapp)
- [The Cat Said No - Python and Flask](https://github.com/luabud/TheCatSaidNo)
