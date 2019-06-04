from flask import request
from microcosm.api import defaults


X_REQUEST = "X-Request"


def context_wrapper(include_header_prefix):
    def retrieve_context():
        return {
            header: value
            for header, value in request.headers.items()
            if header.startswith(include_header_prefix)
        }

    return retrieve_context


@defaults(
    include_header_prefix=X_REQUEST,
)
def configure_request_context(graph):
    """
    Configure the flask context function which controls what data you want to associate
    with your flask request context, e.g. headers, request body/response.

    Usage:
        graph.request_context()

    """
    include_header_prefix = graph.config.request_context.include_header_prefix
    return context_wrapper(include_header_prefix)
