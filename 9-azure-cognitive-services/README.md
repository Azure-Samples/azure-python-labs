# Document recognition with Python Azure Form Recognizer

In this lab, you will learn how to quickly store information you collect from your documents and receipts and prepare them for further analysis.

You will learn to:
- Deploy new resources in Azure
- Write your own code using new Python packages for Azure
- Analyze the information returned from the service

## Prerequisites

- [Azure Subscription](https://azure.microsoft.com/free/)
- macOS, Windows, or Linux
- Python 2.7, or 3.5 or later is required 
- Your favorite editor or [Visual Studio Code](https://code.visualstudio.com/download)

## Create an Azure Form Recognizer resource

[Azure Form Recognizer](https://docs.microsoft.com/azure/cognitive-services/form-recognizer/) is an Azure Cognitive Service focused on using machine learning to identify and extract key-value pairs and table data from scanned paper documents. Applications for Form Recognizer service can extend beyond just assisting with data entry. It could also be used in integrated solutions for optimizing the auditing needs of users, letting them make informed business decisions by learning from their expense trends or matching documents with digital records.

1. Open [Azure Portal](https://portal.azure.com/) and login using your account with an existing Azure subscription.

1. In the top search bar search for Form Recognizer. You will find it in the Marketplace section. https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesFormRecognizer

1. A series of open fields will appear. Enter the following values:

    | Field | Value |
    | --- | --- |
    | Name | **ReceiptAnalyzer**. You can choose your own name, just make sure to change it in your code later |
    | Subscription | Select Active Azure subscription |
    | Location | Select location that works best for you |
    | Pricing tier | **F0** |
    | Resource group | Click on `Create New` and put **receipt-analyzer** as the new name |
    | I confirm I have read and understood the notice below | Check the box|

1. Click create and wait for the deployment to finish. You should be able to see `Go to resource` button once your resource is ready.

1. In the left-hand menu click Keys and Endpoint.

Accessing these values will allow you to get the values necessary for authentication for you to be able to interact with your resource. You will need these values soon so leave this tab open for now

## Start your own application

Open the directory where you will be working and start a new .py file. Open it in your editor

## Install the package

Install the Azure Form Recognizer client library for Python with pip:

```bash
pip install azure-ai-formrecognizer
```

## Authenticate the client

There is a couple of different ways in which you can authenticate, but for now we are going to use the values that you have collected from Azure Portal. If you want to learn more about other ways of authenticating you can read about it [here](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer#authenticate-the-client)

In order to authenticate you will need to collect your credentials from the Azure Portal tab that you opened before. Make sure to replace `<region>` with the `LOCATION` you can see in Azure Portal, and `<api_key>` with the value found in `KEY 1` in Azure Portal.

> Note: Normally, you wouldn't want to store the credentials in your code but rather as environment variables. If you want more information access TODO

```python
endpoint = "https://<region>.api.cognitive.microsoft.com/"
credential = AzureKeyCredential("<api_key>")
```

`FormRecognizerClient` will be your primary way of interacting with your Form Recognizer resource. You will be able to access all of the possible options by just typing `form_recognizer_client.` and choosing the function you want.

For now, we want to focus on recognizing the information in a receipt. In this tutorial we will be focusing on the receipts that are uploaded and you have an url for, but if you want to try analyzing receipts you have on your computer you can find samples for using local files [here](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer#recognize-receipts)

## Write the logic of your application

Replace all of the code that you have in your .py file with the following sample. Make sure to change the two lines at the beginning with the information you retrieved the values for in the previous step.

```python
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

class RecognizeReceiptsFromURLSample(object):

    def recognize_receipts_from_url(self):
        form_recognizer_client = FormRecognizerClient(
            endpoint = "https://<region>.api.cognitive.microsoft.com/", 
            credential=AzureKeyCredential("<api_key>")
        )
        url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-receipt.png"
        poller = form_recognizer_client.begin_recognize_receipts_from_url(url=url)
        receipts = poller.result()

        for idx, receipt in enumerate(receipts):
            print("--------Recognizing receipt #{}--------".format(idx))
            print("Receipt Type: {} has confidence: {}".format(receipt.receipt_type.type, receipt.receipt_type.confidence))
            print("Merchant Name: {} has confidence: {}".format(receipt.merchant_name.value, receipt.merchant_name.confidence))
            print("Transaction Date: {} has confidence: {}".format(receipt.transaction_date.value, receipt.transaction_date.confidence))
            print("Receipt items:")
            for item in receipt.receipt_items:
                print("...Item Name: {} has confidence: {}".format(item.name.value, item.name.confidence))
                print("...Item Quantity: {} has confidence: {}".format(item.quantity.value, item.quantity.confidence))
                print("...Individual Item Price: {} has confidence: {}".format(item.price.value, item.price.confidence))
                print("...Total Item Price: {} has confidence: {}".format(item.total_price.value, item.total_price.confidence))
            print("Subtotal: {} has confidence: {}".format(receipt.subtotal.value, receipt.subtotal.confidence))
            print("Tax: {} has confidence: {}".format(receipt.tax.value, receipt.tax.confidence))
            print("Tip: {} has confidence: {}".format(receipt.tip.value, receipt.tip.confidence))
            print("Total: {} has confidence: {}".format(receipt.total.value, receipt.total.confidence))
            print("--------------------------------------")

if __name__ == '__main__':
    sample = RecognizeReceiptsFromURLSample()
    sample.recognize_receipts_from_url()
```

## Run the app

If you are using the Python extension in VS Code simply click `Ctrl-Alt-N` (Windows or Linux) or `Cmd-Option-N` (macOS). Otherwise just run

```bash
python <name-of-your-file>.py
```

## Explore the results

Congratulations! You have successfully analyzed the receipt information. You should see the values from [your receipt](https://raw.githubusercontent.com/Azure/azure-sdk-for-python/master/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/receipt/contoso-receipt.png) printed right after running your application. You will be able to directly access all of the information and analyze the information. For example you could calculate things like average cost of your transactions etc.

## Next steps

If you are interested in learning more about different things you can do with your Form Recognizer resource, such as writing and training your own models you can find [more documentation here](https://docs.microsoft.com/en-us/azure/cognitive-services/form-recognizer/)

For more samples visit our [GitHub page](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer#more-sample-code)

If you have any feedback for us feel free to [fill this form](https://aka.ms/FR_SDK_v1_feedback)