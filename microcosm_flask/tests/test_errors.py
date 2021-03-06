"""
Error handling tests.

"""
import json
from unittest.mock import patch

from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    has_entry,
    is_,
    starts_with,
)
from microcosm.api import create_object_graph
from werkzeug.exceptions import HTTPException, InternalServerError, NotFound


class MyUnexpectedError(Exception):
    pass


class MyValidationError(Exception):
    code = 400


class MyConflictError(Exception):
    code = 409
    retryable = True

    @property
    def context(self):
        return dict(
            errors=[
                dict(message="Banana!"),
            ],
        )


class NonNumericError(Exception):
    code = "foo"


class AuthenticationError(HTTPException):
    code = 401
    description = "no trespassing"

    def get_headers(self, environ=None):
        return {
            "Content-Type": "application/json",
            "WWW-Authenticate": "Basic realm=outer-zone",
        }


def test_werkzeug_http_error():
    """
    Explicit HTTP errors are reported as expected.

    """
    graph = create_object_graph(name="example", testing=True)

    @graph.app.route("/not_found")
    @graph.audit
    def not_found():
        raise NotFound

    client = graph.app.test_client()

    response = client.get("/not_found")
    assert_that(response.status_code, is_(equal_to(404)))
    data = response.json
    assert_that(data, has_entries(dict(
        code=404,
        context={
            "errors": [],
        },
        message=starts_with("The requested URL was not found on the server."),
        retryable=False,
    )))


def test_no_route():
    """
    Implicit App/Werkzeug errors are reported as expected.

    """
    graph = create_object_graph(name="example", testing=True)

    client = graph.app.test_client()

    response = client.get("/no_route")
    assert_that(response.status_code, is_(equal_to(404)))
    data = response.json
    assert_that(data, has_entries(dict(
        code=404,
        message=starts_with("The requested URL was not found on the server."),
        retryable=False,
        context={"errors": []},
    )))


def test_werkzeug_http_error_custom_message():
    """
    Custom error messages are returned.

    """
    graph = create_object_graph(name="example", testing=True)

    @graph.app.route("/why_me")
    @graph.audit
    def why_me():
        raise InternalServerError("Why me?")

    client = graph.app.test_client()

    response = client.get("/why_me")
    assert_that(response.status_code, is_(equal_to(500)))
    data = response.json
    assert_that(data, has_entries(dict(
        code=500,
        message="Why me?",
        retryable=False,
        context={"errors": []},
    )))


def test_custom_error():
    """
    Custom errors are handled as expected.

    """
    graph = create_object_graph(name="example", testing=True)

    @graph.app.route("/unexpected")
    @graph.audit
    def unexpected():
        raise MyUnexpectedError("unexpected")

    client = graph.app.test_client()

    response = client.get("/unexpected")
    assert_that(response.status_code, is_(equal_to(500)))
    data = response.json
    assert_that(data, has_entries(dict(
        code=500,
        message="unexpected",
        retryable=False,
        context={"errors": []},
    )))


def test_custom_error_status_code():
    """
    Custom errors status codes are handled as expected.

    """
    graph = create_object_graph(name="example", testing=True)

    @graph.app.route("/malformed_syntax")
    @graph.audit
    def malformed_syntax():
        raise MyValidationError

    client = graph.app.test_client()

    with patch("microcosm_flask.errors.send_error_to_sentry") as mock_sentry:
        response = client.get("/malformed_syntax")

    mock_sentry.assert_not_called()
    assert_that(response.status_code, is_(equal_to(400)))
    data = response.json
    assert_that(data, has_entries(dict(
        code=400,
        message="MyValidationError",
        retryable=False,
        context={"errors": []},
    )))


def test_sentry_integration():
    """
    Test when sentry enabled, send_error_to_sentry is called in addition to make_json_error with the
    original exception and the output of make_json_error

    """
    def loader(metadata):
        return dict(
            sentry_logging=dict(
                dsn="topic",
                enabled=True,
            ),
        )
    graph = create_object_graph(name="example", testing=True, loader=loader)

    @graph.app.route("/malformed_syntax")
    @graph.audit
    def malformed_syntax():
        raise MyValidationError

    client = graph.app.test_client()

    with patch("microcosm_flask.errors.send_error_to_sentry") as mock_sentry:
        response = client.get("/malformed_syntax")

    (actual_exception, actual_response), kwargs = mock_sentry.call_args

    assert_that(isinstance(actual_exception, MyValidationError), is_(True))
    assert_that(mock_sentry.call_count, is_(equal_to(1)))
    assert_that(json.loads(actual_response.data), is_(equal_to(response.json)))
    assert_that(response.status_code, is_(equal_to(400)))
    assert_that(response.json, has_entries(dict(
        code=400,
        message="MyValidationError",
        retryable=False,
        context={"errors": []},
    )))


def test_custom_error_retryable():
    """
    Custom errors status codes are handled as expected.

    """
    graph = create_object_graph(name="example", testing=True)

    @graph.app.route("/conflict")
    @graph.audit
    def conflict():
        raise MyConflictError("Conflict")

    client = graph.app.test_client()

    response = client.get("/conflict")
    assert_that(response.status_code, is_(equal_to(409)))
    data = response.json
    assert_that(data, has_entries(dict(
        code=409,
        message="Conflict",
        retryable=True,
        context={
            "errors": [{
                "message": "Banana!",
            }]
        },
    )))


def test_error_wrap():
    """
    Wrapped errors work properly.

    """
    graph = create_object_graph(name="example", testing=True)

    def fail():
        raise Exception("fail")

    @graph.app.route("/wrap")
    @graph.audit
    def wrap():
        try:
            fail()
        except Exception as error:
            raise Exception(error)

    client = graph.app.test_client()

    response = client.get("/wrap")
    assert_that(response.status_code, is_(equal_to(500)))
    data = response.json
    assert_that(data, has_entries(dict(
        code=500,
        message="fail",
        retryable=False,
        context={"errors": []}
    )))


def test_non_numeric_error():
    """
    Explicit HTTP errors are reported as expected.

    """
    graph = create_object_graph(name="example", testing=True)

    @graph.app.route("/foo")
    @graph.audit
    def foo():
        raise NonNumericError("Hello")

    client = graph.app.test_client()

    response = client.get("/foo")
    assert_that(response.status_code, is_(equal_to(500)))
    data = response.json
    assert_that(data, has_entries(dict(
        code=500,
        message="Hello",
        retryable=False,
        context={"errors": []},
    )))


def test_custom_headers():
    """
    Custom headers are sent to the client

    """
    graph = create_object_graph(name="example", testing=True)

    @graph.app.route("/foo")
    @graph.audit
    def foo():
        raise AuthenticationError()

    client = graph.app.test_client()

    response = client.get("/foo")
    data = response.json
    assert_that(data,
                has_entry("message", AuthenticationError.description))
    www_authenticate = response.headers.get('www-authenticate')
    assert_that(www_authenticate, equal_to('Basic realm=outer-zone'))
