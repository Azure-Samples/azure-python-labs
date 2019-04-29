# Use Azure Functions to Find Primes

Create an Azure Function in Python that takes an integer and returns a Boolean value of whether or not the number is prime.

## Use the Azure Functions Command Line Interface (CLI) to create a new Python Azure Function App

Create a directory for the sample code and `cd` into it:

``` powershell
mkdir python_azure_func
cd python_azure_func
```

Create a virtual environment. This is a requirement to create a Python Azure Functions project:  

``` powershell
py -3.6 -m venv .env
.\.env\Scripts\activate
```

Initialize a new Azure Functions App project.

``` powershell
func init prime_calculator
```

Highlight `python (preview)` with the arrow keys in the list of worker runtimes, press `Enter` to select.  You should see output resembling:

``` powershell
Installing wheel package
Installing azure-functions==1.0.0b3 package
Installing azure-functions-worker==1.0.0b4 package
Running pip freeze
Writing .funcignore
Writing .gitignore
Writing host.json
Writing local.settings.json
Writing path\to\prime_calculator\.vscode\extensions.json
```

A new folder named `prime_calculator` is created. Change directory into this folder:

``` powershell
cd prime_calculator
```

## Create an HTTP Triggered Azure Function

Execute the following command to create a new Azure Function in your app:

``` powershell
func new
```

Highlight `HTTP trigger` with the arrow keys in the list of templates, press `Enter` to select.

> Note: if you get the error
> `Unable to find project root. Expecting to find one of host.json, local.settings.json in project root.`
> you likely need to change directory into the project directory, `cd prime_calculator`.

You will be prompted to name your function:

``` powershell
Function name: [HttpTrigger]
```

Name your function `is_prime`. Hit `Enter` and the CLI will create the files for this Function. The Function App file structure should now look like this:

``` powershell
prime_calculator
│   .funcignore         # Functions listed here will be excluded from deployment
│   .gitignore          # files and directories not to be checked into source control
│   host.json           # runtime settings, including which version of Azure Functions to use
│   local.settings.json # included in the .gitignore by default, these settings will be used when running locally
│   requirements.txt    # modules required to be installed for running the Function App
│
├───.vscode
│       extensions.json # read by VSCode to set extensions
│
└───is_prime            # directory holding all files for our `is_prime` Function
        function.json   # defines that __init__.py will be called and which bindings are used
        sample.dat      # contains a sample input for the Function
        __init__.py     # this module will be called when the Function is run
```

The default Function created for HTTPTrigger will take a `name` argument and greet the user.  

## Testing the Default Function in the Browser

To run the app locally, execute:

``` powershell
func host start
```

Once running, you should see:

``` powershell
Http Functions:

        is_prime: [GET,POST] http://localhost:7071/api/is_prime
```

This lists the endpoints made available by the app. In this case, only one URL `http://localhost:7071/api/is_prime` which will run the `is_prime` Function and accepts two HTTP methods, `GET` and `POST`.

To test the app, open any browser and go to the given URL. You should see a plain HTML page with the text `Please pass a name on the query string or in the request body`. Change the URL so that it reads `http://localhost:7071/api/is_prime?name=PyCon`. The page at this URL should display the text `Hello PyCon!`.

> Note: If you are not seeing the correct response here, it would be a good time to ask for assistance. Understanding how to pass values to the Function using a query string is important for the rest of the lab.

Before moving on, shut down the app. In the command prompt, type `ctrl+c`, you will be asked to confirm `Terminate batch job (Y/N)?`. Respond with `Y`.

## Writing is_prime

Execute `code .` to open the Azure Functions App in Visual Studio Code. In the app, open the file `prime_calculator/is_prime/__init__.py`.

This is the code you ran in the section above. If the HTTP endpoint receives a query string with a value mapping to the key `name` it returns `Hello {name}!`. Otherwise, it returns a 400 code with an error message.

Edit this code to add a function that calculates if an integer is a prime number. In the `__init__.py` file, add to the top of the file:

``` python
import math
```

and to the bottom of the file:

``` python
def is_prime(number: int) -> bool:
    """Tests primeness of number, returns true if prime."""
    min_divisor = 2
    max_divisor = math.ceil(math.sqrt(number))
    for divisor in range(min_divisor, max_divisor + 1):
        if number % divisor == 0:
            return False
    return True
```

Edit the `main` function in `__init__.py` to take an `int` as input and check if it's a prime number or not with the function.

``` python
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    number = req.params.get('number')
    try:
        number = int(number)
    except TypeError:
        return func.HttpResponse(
             "Please pass an integer corresponding to the key `number` on the query string or in the request body",
             status_code=400
        )

    response = "is prime" if is_prime(number) else "is composite"
    return func.HttpResponse(f"{number} {response}.")
```

Save the file and return to the terminal. To run the updated Azure Function App, execute:

``` powershell
func host start
```

Once running, you should see:  

``` powershell
Http Functions:

        is_prime: [GET,POST] http://localhost:7071/api/is_prime
```

Visit the URL in a browser. You should get the response "Please pass an integer corresponding to the key \`number\` on the query string or in the request body". Try passing the Azure Function an integer by visiting the URL:

``` url
http://localhost:7071/api/is_prime?number=9
```

You should get the response "9 is composite".

## Next Steps

- [Sample app similar to this lab: Create your first Python Function in Azure](https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-python)
- [Blog: Taking a closer look at Python support for Azure Functions](https://azure.microsoft.com/en-us/blog/taking-a-closer-look-at-python-support-for-azure-functions/)
- [Azure Functions Python Worker is Open Source on GitHub](https://github.com/Azure/azure-functions-python-worker)
