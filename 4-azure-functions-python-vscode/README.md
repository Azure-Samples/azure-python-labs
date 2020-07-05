# Sentiment analysis with Python Azure Functions

In this lab, you will build a serverless HTTP API with Azure Functions that takes a sentence as an input and returns the sentiment of the sentence.

You will learn to:
- Build a serverless HTTP API with Azure Functions
- Run and debug the API locally on your machine
- Deploy the API to Azure Functions

## Prerequisites

- macOS, Windows, or Linux
- Python 3.6, 3.7, or 3.8
- [Visual Studio Code](https://code.visualstudio.com/download) with these extensions installed:
    - [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
    - [Azure Functions](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions)

## Create an Azure Functions app and a new function

Azure Functions allows you to build and deploy your code as functions, without worrying about managing servers and other infrastructure. Your functions are triggered by events such as: items added on a queue, a document updated in a database, or an HTTP request.

You will build an HTTP API using an Azure Function. An Azure Functions app can contain one or more Azure Functions.

1. Open a new VS Code window.

1. Open the command palette by pressing `F1`, `Ctrl-Shift-P` (Windows or Linux), `Cmd-Shift-P` (macOS).

1. Search for and select **Azure Functions: Create new project...**.

1. Browse to a location where you want to create your project. Create a new empty folder and click **Select** to open it.

1. A series of prompts will appear. Enter the following values:

    | Prompt | Value | Description |
    | --- | --- | --- |
    | Language for your project | **Python** | |
    | Python interpreter | Select one | Azure Functions requires Python 3.6, 3.7, 3.8 |
    | Template for your first function | **HTTP trigger** | |
    | Function name | **sentiment** | |
    | Authorization level | **anonymous** | Allow function to be accessed anonymously |
    | How to open new project | **Open in current window** | |

VS Code reopens in the function app. Here are some important files and folders that you'll need to know for this lab:
- `.venv/` - A virtual environment is automatically created for you using the version of Python you selected. When running your function app, it runs in this virtual environment.
- `.vscode/` - VS Code settings, including the tasks needed to run and debug the function app.
- `sentiment/`
    - `__init__.py` - Your new function
    - `function.json` - Metadata for your function
- `requirements.txt` - Contains Python dependencies for your app

## Modify the function to perform sentiment analysis

1. From the VS Code explorer, open `requirements.txt`.

1. You will use the [VADER Sentiment Analysis](https://github.com/cjhutto/vaderSentiment) library in your app. On a new line in `requirements.txt`, add `vaderSentiment`.

    This will cause VS Code to install the package when you run the function app in the next section.

1. Open the function at `sentiment/__init__.py`.

1. Replace the body of the file with the following code that uses the VADER library to perform sentiment analysis on some input text that is passed to the function and returns the result:

    ```python
    import azure.functions as func
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


    def main(req: func.HttpRequest) -> func.HttpResponse:
        analyzer = SentimentIntensityAnalyzer()
        text = req.params.get("text")
        scores = analyzer.polarity_scores(text)
        sentiment = "positive" if scores["compound"] > 0 else "negative"
        return func.HttpResponse(sentiment)
    ```

## Run and debug the app

1. Start debugging in VS Code by pressing `F5` or by selecting **Debug: Start debugging** from the command palette.

1. If you don't have the Azure Functions Core Tools installed, VS Code will prompt you to install it. Select **Install**.

    > If the installation fails, follow [these instructions](https://github.com/Azure/azure-functions-core-tools#installing) to install it. Note: Azure Functions Core Tools Version 3 is compatible with Python3.8, if you're using 3.7 or 3.6 use the version2 command line to install.

1. Once the function app has started, open your web browser and enter the following in the address bar to run your function:

    ```
    http://localhost:7071/api/sentiment?text=I+love+PyCon
    ```

    It should return a result of `positive`.

1. In `sentiment/__init__.py`, set a breakpoint by placing your cursor on the first line in the function and pressing `F9`.

1. Return to your browser and enter the above URL again (or you can replace the `text` query string with a sentence of your own).

    VS Code should stop on the breakpoint. You can step through the code with `F10` and inspect the values of variables.

1. Stop debugging by pressing `Shift-F5`.

## Deploy the app to Azure

You will now use VS Code to deploy the function app to Azure.

1. In the command palette, search for and select **Azure Functions: Deploy to Function App**.

1. When prompted to select a subscription, select **Sign in to Azure**.

1. The browser should open to the Azure sign in page. Log in with your Azure credentials.

1. Enter the following values in the prompts:

    | Prompt | Value | Description |
    | --- | --- | --- |
    | Select subscription | Your Azure subscription | If you were provided credentials for the lab, select the subscription that appears |
    | Select Function App | **Create new Function App in Azure (Advanced)** | Ensure you select the **Advanced** option so you can choose the resource group to deploy to |
    | Select a runtime | A Python version | Select the same version as you used to create your local function app |
    | Select a hosting plan | **Consumption** | |
    | Select a resource group | A resource group | If you were provided lab credentials, you must select the existing resource group from the dropdown |
    | Select a storage account | **Create a new storage account** | Azure Functions requires a storage account to store your code |
    | Name of storage account | Accept the default name | |
    | Select an Application Insights | **Create new Application Insights** | Application Insights provides monitoring for your function app |
    | Name of Application Insights | Accept the default name | |
    | Location | **Central US** | |

    Wait for the resources to be provisioned and your app to be deployed.

1. When the deployment is complete, A prompt should appear. Click on **View output**.

    > If you were not prompted to view the output, open the Output window manually by pressing `Ctrl-Shift-U` (`Cmd-Shift-U` on macOS). Select **Azure Functions** from the dropdown.

1. In the output, locate the HTTP trigger URL, it should look like `https://<function-app-name>.azurewebsites.net/api/sentiment`.

    Copy it and paste it into your browser's address bar. Append `?text=I+love+PyCon` to the end of the URL and press enter.

    You should see the sentiment returned.

Congratulations! You have deployed an HTTP API using Azure Functions!
