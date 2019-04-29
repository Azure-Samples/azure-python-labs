import math
import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    number = req.params.get("number")
    try:
        number = int(number)
    except TypeError:
        return func.HttpResponse(
            "Please pass an integer corresponding to the key `number` on the query string.",
            status_code=400,
        )

    response = "is prime" if is_prime(number) else "is composite"
    return func.HttpResponse(f"{number} {response}.")


def is_prime(number: int) -> bool:
    """Tests primeness of number, returns true if prime."""
    min_divisor = 2
    max_divisor = math.ceil(math.sqrt(number))
    for divisor in range(min_divisor, max_divisor + 1):
        if number % divisor == 0:
            return False
    return True
