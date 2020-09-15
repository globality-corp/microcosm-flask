from flask import request
from microcosm.api import defaults


X_REQUEST = "X-Request"
HEADER_PREFIXES = [X_REQUEST]


def context_wrapper(include_header_prefixes):
    def retrieve_context():
        context = {
            header: value
            for header, value in request.headers.items()
            if any([
                header.lower().startswith(prefix.lower())
                for prefix in include_header_prefixes
            ])
        }
        return context
    return retrieve_context


@defaults(
    include_header_prefixes=HEADER_PREFIXES,
)
def configure_request_context(graph):
    """
    Configure the flask context function which controls what data you want to associate
    with your flask request context, e.g. headers, request body/response.

    Usage:
        graph.request_context()

    """
    include_header_prefixes = graph.config.request_context.include_header_prefixes
    return context_wrapper(include_header_prefixes)
