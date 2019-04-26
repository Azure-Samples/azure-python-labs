import json
import sys
import os


def get_api_key():
    try:
        with open("local.settings.json", "r") as settings:
            return json.loads(settings.read())["key1"]
    except FileNotFoundError:
        raise FileNotFoundError(
            "You may not have created a `local.settings.json` file. See LAB_SETUP.md for instructions."
        )
