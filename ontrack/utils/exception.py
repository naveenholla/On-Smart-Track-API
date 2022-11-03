from django.http import JsonResponse
from requests import ConnectionError
from rest_framework.views import exception_handler

from ontrack.utils.logger import ApplicationLogger


class Error_While_Data_Pull(Exception):
    pass


logger = ApplicationLogger()


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data["status_code"] = response.status_code

    # checks if the raised exception is of the type you want to handle
    if isinstance(exc, ConnectionError):
        # defines custom response data
        err_data = {"MSG_HEADER": "some custom error messaging"}

        # logs detail data from the exception being handled
        message = f"Original error detail and callstack: {exc}"
        logger.log_critical(message=message)

        # returns a JsonResponse
        return JsonResponse(err_data, safe=False, status=503)

    # returns response as handled normally by the framework
    return response
