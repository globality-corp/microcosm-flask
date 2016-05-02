"""
Audit log support for Flask routes.

"""
from logging import getLogger
from functools import wraps
from json import loads
from traceback import format_exc

from flask import current_app, g, request

from microcosm_flask.errors import (
    extract_context,
    extract_error_message,
    extract_status_code,
)


def audit(func):
    """
    Record a Flask route function in the audit log.

    Generates a JSON record in the Flask log for every request.

    """
    logger = getLogger("audit")

    @wraps(func)
    def wrapper(*args, **kwargs):
        response = None
        request_id = request.headers.get('X-Request-Id', 'None')

        # always include these fields
        audit_dict = dict(
            operation=request.endpoint,
            func=func.__name__,
            method=request.method,
        )
        audit_dict.update({"X-Request-Id": request_id})

        # include request body on debug (if any)
        if current_app.debug and request.get_json(force=True, silent=True):
            audit_dict["request_body"] = request.get_json(force=True)

        try:
            response = func(*args, **kwargs)
        except Exception as error:
            status_code = extract_status_code(error)
            success = 0 < status_code < 400
            audit_dict.update(
                success=success,
                message=extract_error_message(error)[:2048],
                context=extract_context(error),
                stack_trace=None if success else format_exc(limit=10),
                status_code=status_code,
            )
            raise
        else:
            body, status_code = parse_response(response)

            audit_dict.update(
                success=True,
                status_code=status_code,
            )

            # include response body on debug (if any)
            if current_app.debug and body and not g.get("hide_body"):
                try:
                    audit_dict["response_body"] = loads(body)
                except (TypeError, ValueError):
                    # not json
                    audit_dict["response_body"] = body

            return response
        finally:
            # always log at INFO; we can't know whether a raised exception
            # is an error or expected behavior
            logger.info(audit_dict)

    return wrapper


def parse_response(response):
    """
    Parse a Flask response into a body and status code.

    The returned value from a Flask view could be:
        * a tuple of (response, status) or (response, status, headers)
        * a Response object
        * a string
    """
    if isinstance(response, tuple) and len(response) > 1:
        return response[0], response[1]
    try:
        return response.data, response.status_code
    except AttributeError:
        return response, 200


def configure_audit_decorator(graph):
    """
    Configure the audit decorator.

    Example Usage:

        @graph.audit
        def login(username, password):
            ...
    """
    return audit
