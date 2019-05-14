from flask import request


# Special headers reserved for use in `microcosm-` based applications:
ALL_HEADER_LIST = (
    "X-Request",  # These are values *invariant* to a user request from UI
                  # perspective, e.g. user-id, request-id, etc.
    "X-Client",   # These are values *specific* to a single HTTP Client call to a web service
)

# This is the list of internal Headers which should always be logged.
LOGGABLE_HEADER_WHITE_LIST = ("X-Request")


def make_get_request_context(header_white_list=LOGGABLE_HEADER_WHITE_LIST):
    def get_request_context():
        return {
            header: value
            for prefix in header_white_list
            for header, value in request.headers.items()
            if header.startswith(prefix)
        }
    return get_request_context
