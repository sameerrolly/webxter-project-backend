"""
Custom DRF exception handler.

Normalises all error responses into a consistent shape:
  {
    "error":   true,
    "status":  <http_status_code>,
    "message": "<human readable summary>",
    "details": <original DRF error dict>   ← only present when there are field errors
  }

This makes it trivial to handle errors uniformly in the React frontend.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    # Let DRF build the default response first
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception — let Django's 500 handler deal with it
        return None

    http_status = response.status_code
    data        = response.data

    # Extract a human-readable message
    if isinstance(data, dict):
        message = (
            data.get("detail")
            or data.get("non_field_errors", [None])[0]
            or next(iter(data.values()), "An error occurred.")
        )
        # If message is a list, take the first item
        if isinstance(message, list):
            message = message[0]
        message = str(message)
    elif isinstance(data, list):
        message = str(data[0]) if data else "An error occurred."
    else:
        message = str(data)

    normalised = {
        "error":   True,
        "status":  http_status,
        "message": message,
    }

    # Include field-level details when it's a validation error (400)
    if http_status == status.HTTP_400_BAD_REQUEST and isinstance(data, dict):
        normalised["details"] = data

    response.data = normalised
    return response
