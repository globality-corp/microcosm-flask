"""
Support for request forwarding.

HATEOAS depends heavily on services being able to generate URIs back to their own resources.
Under some request forwarding scenarios (especially AWS ALBs), services may not be resolved
on a URI that is accessible to other services. This can be solved by configuring static
service URIs... or by resolving URIs using X-Forwarded headers.

"""
from flask import request, _request_ctx_stack

from microcosm_flask.session import register_session_factory


def use_forwarded_port(graph):
    """
    Inject the `X-Forwarded-Port` (if any) into the current URL adapter.

    The URL adapter is used by `url_for` to build a URLs.

    """
    # There must be a better way!
    context = _request_ctx_stack.top

    if _request_ctx_stack is None:
        return None

    # determine the configured overrides
    forwarded_host = graph.config.port_forwarding.get("host")
    forwarded_port = request.headers.get("X-Forwarded-Port")

    if not forwarded_port and not forwarded_host:
        return None

    # determine the current server name
    if ":" in context.url_adapter.server_name:
        server_host, server_port = context.url_adapter.server_name.split(":", 1)
    else:
        server_host = context.url_adapter.server_name
        server_port = 443 if context.url_adapter.url_scheme == "https" else 80

    # choose a new server name
    if forwarded_host:
        server_name = forwarded_host
    elif server_port:
        server_name = "{}:{}".format(server_host, forwarded_port)
    else:
        server_name = "{}:{}".format(server_host, server_port)

    context.url_adapter.server_name = server_name
    return server_name


def configure_port_forwarding(graph):
    """
    Bind the SQLAlchemy session context to Flask.

    The current session is available at `g.db.session`.

    """
    return register_session_factory(graph, "forwarded_port", use_forwarded_port)
