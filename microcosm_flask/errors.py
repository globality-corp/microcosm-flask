"""
Generalized error handling.

"""
from logging import getLogger

from marshmallow import Schema, fields
from werkzeug.exceptions import default_exceptions

from microcosm_flask.conventions.encoding import dump_response_data


error_logger = getLogger("errors")


class SubErrorSchema(Schema):
    message = fields.String(required=True)


class ErrorContextSchema(Schema):
    errors = fields.List(fields.Nested(SubErrorSchema), required=True)


class ErrorSchema(Schema):
    message = fields.String(required=True, default="Unknown Error")
    code = fields.Integer(required=True, default=500)
    retryable = fields.Boolean(required=True, default=False)
    context = fields.Nested(ErrorContextSchema, required=False)


def as_retryable(error):
    """
    Given an exception, mark it as retryable when serializing
    into HTTP error response.

    """
    error.retryable = True

    return error


def extract_status_code(error):
    """
    Extract an error code from a message.

    """
    try:
        return int(error.code)
    except (AttributeError, TypeError, ValueError):
        try:
            return int(error.status_code)
        except (AttributeError, TypeError, ValueError):
            try:
                return int(error.errno)
            except (AttributeError, TypeError, ValueError):
                return 500


def extract_error_message(error):
    """
    Extract a useful message from an error.

    Prefer the description attribute, then the message attribute, then
    the errors string conversion. In each case, fall back to the error class's
    name in the event that the attribute value was set to a uselessly empty string.

    """
    try:
        return error.description or error.__class__.__name__
    except AttributeError:
        try:
            return str(error.message) or error.__class__.__name__
        except AttributeError:
            return str(error) or error.__class__.__name__


def extract_context(error):
    """
    Extract extract context from an error.

    Errors may (optionally) provide a context attribute which will be encoded
    in the response.

    """
    return getattr(error, "context", {"errors": []})


def extract_retryable(error):
    """
    Extract a retryable status from an error.

    It's not usually helpful to retry on an error, but it's useful to do so
    when the application knows it might.

    """
    return getattr(error, "retryable", False)


def extract_headers(error):
    """
    Extract HTTP headers to include in response.

    """
    try:
        return error.headers
    except AttributeError:
        try:
            return error.get_headers()
        except (AttributeError, TypeError):
            return {}


def extract_include_stack_trace(error):
    """
    Extract whether error should include a stack trace.

    """
    return getattr(error, "include_stack_trace", True)


def make_json_error(error):
    """
    Handle errors by logging and
    """
    message = extract_error_message(error)
    status_code = extract_status_code(error)
    context = extract_context(error)
    retryable = extract_retryable(error)
    headers = extract_headers(error)

    # Flask will not log user exception (fortunately), but will log an error
    # for exceptions that escape out of the application entirely (e.g. if the
    # error handler raises an error)
    error_logger.debug("Handling {} error: {}".format(
        status_code,
        message,
    ))

    # Serialize into JSON response
    response_data = {
        "code": status_code,
        "context": context,
        "message": message,
        "retryable": retryable,
    }
    # Don't pass in the error schema because it will suppress any extra fields
    return dump_response_data(None, response_data, status_code, headers)


def configure_error_handlers(graph):
    """
    Register error handlers.

    """
    # override all of the werkzeug HTTPExceptions
    for code in default_exceptions.keys():
        graph.flask.register_error_handler(code, make_json_error)

    # register catch all for user exceptions
    graph.flask.register_error_handler(Exception, make_json_error)
