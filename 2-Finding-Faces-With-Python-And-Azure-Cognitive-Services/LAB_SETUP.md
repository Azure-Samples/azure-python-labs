# Detecting Emotion with Azure Cognitive Services (ACS) Lab Setup

## Requirements

- An Azure Cognitive Services API Key. You can get a free key for 7 days at this [link](https://azure.microsoft.com/en-us/try/cognitive-services/?api=face-api).
- Python pip requirements that can be installed globally or to a virtual environment by running `pip install requirements.txt` in the same directory as this file.

## Setting Up the Developer Environment

By default, when you set up your ACS API, you should get two keys. Create a file in the same directory as this file called `local.settings.json`. The file will be gitignored by default. This file will be where we keep our secret keys - editing the `.gitignore` can compromise the privacy of these keys. If you suspect the keys have been deployed to a public repository, the keys can be reset from the Azure portal.

You can get your keys from the Azure portal or using the Azure CLI by running: 

``` powershell
az cognitiveservices account keys list -g <RESOURCE_GROUP_NAME> -n <RESOURCE_NAME>
```

This will return a json resembling: 

``` json
{
  "key1": "<KEY>",
  "key2": "<KEY>"
}
```

Copy this output to the `local.settings.json` file and you are all set!

