"""
Error handling tests.

"""
from json import loads

from hamcrest import assert_that, equal_to, has_entry, is_
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
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to({
        "code": 404,
        "message": "The requested URL was not found on the server.  "
                   "If you entered the URL manually please check your spelling and try again.",
        "retryable": False,
        "context": {"errors": []},
    })))


def test_no_route():
    """
    Implicit App/Werkzeug errors are reported as expected.

    """
    graph = create_object_graph(name="example", testing=True)

    client = graph.app.test_client()

    response = client.get("/no_route")
    assert_that(response.status_code, is_(equal_to(404)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to({
        "code": 404,
        "message": "The requested URL was not found on the server.  "
                   "If you entered the URL manually please check your spelling and try again.",
        "retryable": False,
        "context": {"errors": []},
    })))


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
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to({
        "code": 500,
        "message": "Why me?",
        "retryable": False,
        "context": {"errors": []},
    })))


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
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to({
        "code": 500,
        "message": "unexpected",
        "retryable": False,
        "context": {"errors": []},
    })))


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

    response = client.get("/malformed_syntax")
    assert_that(response.status_code, is_(equal_to(400)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to({
        "code": 400,
        "message": "MyValidationError",
        "retryable": False,
        "context": {"errors": []},
    })))


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
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to({
        "code": 409,
        "message": "Conflict",
        "retryable": True,
        "context": {
            "errors": [{
                "message": "Banana!",
            }]
        },
    })))


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
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to({
        "code": 500,
        "message": "fail",
        "retryable": False,
        "context": {"errors": []}
    })))


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
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to({
        "code": 500,
        "message": "Hello",
        "retryable": False,
        "context": {"errors": []},
    })))


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
    data = loads(response.get_data())
    assert_that(data,
                has_entry("message", AuthenticationError.description))
    www_authenticate = response.headers.get('www-authenticate')
    assert_that(www_authenticate, equal_to('Basic realm=outer-zone'))
