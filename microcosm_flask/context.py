from flask import request

# This is the total set of Globality-proprietary headers
ALL_HEADER_LIST = (
    "X-Request",  # These are values *invariant* to a user request, e.g. user-id, request-id, etc.
    "X-Client",  # These are values *specific* to a single HTTP Client call to a web service
)

# This is the list of internal Globality Headers we use which are safe for logging.
LOGGABLE_HEADER_WHITE_LIST = ("X-Request")


def get_request_context(header_white_list=LOGGABLE_HEADER_WHITE_LIST):
    return {
        header: value
        for prefix in header_white_list
        for header, value in request.headers.items()
        if header.startswith(prefix)
    }
