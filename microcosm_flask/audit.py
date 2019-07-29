"""
Audit log support for Flask routes.

"""
from collections import namedtuple
from contextlib import contextmanager
from distutils.util import strtobool
from functools import wraps
from json import loads
from logging import DEBUG, getLogger
from traceback import format_exc
from uuid import UUID

from flask import current_app, g, request
from inflection import underscore
from microcosm.api import defaults, typed
from microcosm.config.types import boolean
from microcosm_logging.timing import elapsed_time

from microcosm_flask.errors import (
    extract_context,
    extract_error_message,
    extract_include_stack_trace,
    extract_status_code,
)


DEFAULT_INCLUDE_REQUEST_BODY = 400
DEFAULT_INCLUDE_RESPONSE_BODY = 400


AuditOptions = namedtuple("AuditOptions", [
    "include_request_body",
    "include_response_body",
    "include_path",
    "include_query_string",
    "log_as_debug",
])


SKIP_LOGGING = "_microcosm_flask_skip_audit_logging"


def is_uuid(value):
    try:
        UUID(value)
        return True
    except Exception:
        return False


def skip_logging(func):
    """
    Decorate a function so logging will be skipped.

    """
    setattr(func, SKIP_LOGGING, True)
    return func


def should_skip_logging(func):
    """
    Should we skip logging for this handler?

    """
    disabled = strtobool(request.headers.get("x-request-nolog", "false"))
    return disabled or getattr(func, SKIP_LOGGING, False)


@contextmanager
def logging_levels():
    """
    Context manager to conditionally set logging levels.

    Supports setting per-request debug logging using the `X-Request-Debug` header.

    """
    enabled = strtobool(request.headers.get("x-request-debug", "false"))
    level = None
    try:
        if enabled:
            level = getLogger().getEffectiveLevel()
            getLogger().setLevel(DEBUG)
        yield
    finally:
        if enabled:
            getLogger().setLevel(level)


def audit(func):
    """
    Record a Flask route function in the audit log.

    Generates a JSON record in the Flask log for every request.

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        options = AuditOptions(
            include_request_body=DEFAULT_INCLUDE_REQUEST_BODY,
            include_response_body=DEFAULT_INCLUDE_RESPONSE_BODY,
            include_path=True,
            include_query_string=True,
        )
        with logging_levels():
            return _audit_request(options, func, None, *args, **kwargs)

    return wrapper


class RequestInfo:
    """
    Capture of key information for requests.

    """
    def __init__(self, options, func, request_context):
        self.options = options
        self.operation = request.endpoint
        self.func = func.__name__
        self.method = request.method
        self.args = request.args
        self.view_args = request.view_args
        self.request_context = request_context
        self.timing = dict()

        self.error = None
        self.stack_trace = None
        self.request_body = None
        self.response_body = None
        self.response_headers = None
        self.status_code = None
        self.success = None

    def to_dict(self):
        dct = dict(
            operation=self.operation,
            func=self.func,
            method=self.method,
            **self.timing
        )
        if self.options.include_path and self.view_args:
            dct.update({
                key: value
                for key, value in self.view_args.items()
            })
        if self.options.include_query_string and self.args:
            dct.update({
                key: values[0]
                for key, values in self.args.lists()
                if len(values) == 1 and is_uuid(values[0])
            })

        if self.request_context is not None:
            dct.update(self.request_context())

        if self.success is True:
            dct.update(
                success=self.success,
                status_code=self.status_code,
            )
        if self.success is False:
            dct.update(
                success=self.success,
                message=extract_error_message(self.error)[:2048],
                context=extract_context(self.error),
                stack_trace=self.stack_trace,
                status_code=self.status_code,
            )

        self.post_process_request_body(dct)
        self.post_process_response_body(dct)
        self.post_process_response_headers(dct)

        return dct

    def log(self, logger):
        if self.status_code == 500:
            # something actually went wrong; investigate
            dct = self.to_dict()

            if current_app.debug or current_app.testing:
                message = dct.pop("message")
                logger.warning(message, extra=dct, exc_info=True)
            else:
                logger.warning(dct)
        else:
            # usually log at INFO; a raised exception can be an error or
            # expected behavior (e.g. 404)
            if not self.options.log_as_debug:
                logger.info(self.to_dict())
            else:
                logger.debug(self.to_dict())

    def capture_request(self):
        if not current_app.debug:
            # only capture request body on debug
            return

        if not self.options.include_request_body:
            # only capture request body if requested
            return

        if (
                request.content_length and
                self.options.include_request_body is not True and
                request.content_length >= self.options.include_request_body
        ):
            # don't capture request body if it's too large
            return

        if not request.get_json(force=True, silent=True):
            # only capture request body if json
            return

        self.request_body = request.get_json(force=True)

    def capture_response(self, response):
        self.success = True

        body, self.status_code, self.response_headers = parse_response(response)

        if not current_app.debug:
            # only capture responsebody on debug
            return

        if not self.options.include_response_body:
            # only capture response body if requested
            return

        if not body:
            # only capture request body if there is one
            return

        if (
                self.options.include_response_body is not True and
                len(body) >= self.options.include_response_body
        ):
            # don't capture response body if it's too large
            return

        try:
            self.response_body = loads(body)
        except (TypeError, ValueError):
            # not json
            pass

    def capture_error(self, error):
        self.error = error
        self.status_code = extract_status_code(error)
        self.success = 0 < self.status_code < 400
        include_stack_trace = extract_include_stack_trace(error)
        self.stack_trace = format_exc(limit=10) if (not self.success and include_stack_trace) else None

    def post_process_request_body(self, dct):
        if g.get("hide_body") or not self.request_body:
            return

        for name, new_name in g.get("show_request_fields", {}).items():
            try:
                value = self.request_body.pop(name)
                self.request_body[new_name] = value
            except KeyError:
                pass

        for field in g.get("hide_request_fields", []):
            try:
                del self.request_body[field]
            except KeyError:
                pass

        dct.update(
            request_body=self.request_body,
        )

    def post_process_response_body(self, dct):
        if g.get("hide_body") or not self.response_body:
            return

        for name, new_name in g.get("show_response_fields", {}).items():
            try:
                value = self.response_body.pop(name)
                self.response_body[new_name] = value
            except KeyError:
                pass

        for field in g.get("hide_response_fields", []):
            try:
                del self.response_body[field]
            except KeyError:
                pass

        dct.update(
            response_body=self.response_body,
        )

    def post_process_response_headers(self, dct):
        """
        Rewrite X-<>-Id header into audit logs.
        """
        if not self.response_headers:
            return

        for key, value in self.response_headers.items():
            parts = key.split("-")
            if len(parts) != 3:
                continue
            if parts[0] != "X":
                continue
            if parts[-1] != "Id":
                continue

            dct["{}_id".format(underscore(parts[1]))] = value


def _audit_request(options, func, request_context, *args, **kwargs):  # noqa: C901
    """
    Run a request function under audit.

    """
    logger = getLogger("audit")

    request_info = RequestInfo(options, func, request_context)
    response = None

    request_info.capture_request()
    try:
        # process the request
        with elapsed_time(request_info.timing):
            response = func(*args, **kwargs)
    except Exception as error:
        request_info.capture_error(error)
        raise
    else:
        request_info.capture_response(response)
        return response
    finally:
        if not should_skip_logging(func):
            request_info.log(logger)


def parse_response(response):
    """
    Parse a Flask response into a body, a status code, and headers

    The returned value from a Flask view could be:
        * a tuple of (response, status) or (response, status, headers)
        * a Response object
        * a string
    """
    if isinstance(response, tuple):
        if len(response) > 2:
            return response[0], response[1], response[2]
        elif len(response) > 1:
            return response[0], response[1], {}
    try:
        return response.data, response.status_code, response.headers
    except AttributeError:
        return response, 200, {}


@defaults(
    include_request_body=typed(type=int, default_value=DEFAULT_INCLUDE_REQUEST_BODY),
    include_response_body=typed(type=int, default_value=DEFAULT_INCLUDE_RESPONSE_BODY),
    include_path=typed(type=boolean, default_value=False),
    include_query_string=typed(type=boolean, default_value=False),
    log_as_debug=typed(type=boolean, default_value=False),
)
def configure_audit_decorator(graph):
    """
    Configure the audit decorator.

    Example Usage:

        @graph.audit
        def login(username, password):
            ...
    """
    def _audit(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            options = AuditOptions(
                include_request_body=graph.config.audit.include_request_body,
                include_response_body=graph.config.audit.include_response_body,
                include_path=graph.config.audit.include_path,
                include_query_string=graph.config.audit.include_query_string,
                log_as_debug=graph.config.audit.log_as_debug,
            )
            return _audit_request(options, func, graph.request_context, *args, **kwargs)
        return wrapper
    return _audit
