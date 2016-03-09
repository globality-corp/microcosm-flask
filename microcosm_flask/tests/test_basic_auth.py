"""
Basic Auth tests.

"""
from json import loads

from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm.api import create_object_graph
from microcosm_flask.basic_auth import encode_basic_auth


def test_basic_auth():
    """
    Basic auth prevents resource access.

    """
    config = {
        "BASIC_AUTH_REALM": "microcosm",
    }

    graph = create_object_graph(name="example", testing=True, loader=lambda metadata: config)

    @graph.app.route("/unauthorized")
    @graph.audit
    @graph.basic_auth.required
    def unauthorized():
        raise Exception("Should not be raised!")

    client = graph.app.test_client()

    response = client.get("/unauthorized")
    assert_that(response.status_code, is_(equal_to(401)))
    data = loads(response.get_data())
    assert_that(data, is_(equal_to({
        "message": "The server could not verify that you are authorized to access the URL requested.  "
                   "You either supplied the wrong credentials (e.g. a bad password), or your browser "
                   "doesn't understand how to supply the credentials required.",
        "retryable": False,
        "context": {},
    })))
    assert_that(response.headers["WWW-Authenticate"], is_(equal_to('Basic realm="microcosm"')))


def test_basic_auth_default_realm():
    """
    Basic auth uses the convention that the metadata's name is the realm.

    """
    graph = create_object_graph(name="example", testing=True)

    @graph.app.route("/unauthorized")
    @graph.audit
    @graph.basic_auth.required
    def unauthorized():
        raise Exception("Should not be raised!")

    client = graph.app.test_client()

    response = client.get("/unauthorized")
    assert_that(response.status_code, is_(equal_to(401)))
    data = loads(response.get_data())
    assert_that(data, is_(equal_to({
        "message": "The server could not verify that you are authorized to access the URL requested.  "
                   "You either supplied the wrong credentials (e.g. a bad password), or your browser "
                   "doesn't understand how to supply the credentials required.",
        "retryable": False,
        "context": {},
    })))
    assert_that(response.headers["WWW-Authenticate"], is_(equal_to('Basic realm="example"')))


def test_basic_auth_default_credentials():
    """
    Basic auth default credentials work.

    """
    graph = create_object_graph(name="example", testing=True)

    @graph.app.route("/ok")
    @graph.audit
    @graph.basic_auth.required
    def unauthorized():
        return "OK"

    client = graph.app.test_client()

    response = client.get("/ok", headers={
        "Authorization": encode_basic_auth("default", "secret"),
    })
    assert_that(response.status_code, is_(equal_to(200)))


def test_basic_auth_custom_credentials():
    """
    Basic auth default credentials work.

    """
    config = dict(
        basic_auth=dict(
            credentials=dict(
                username="password",
            )
        )
    )

    graph = create_object_graph(name="example", testing=True, loader=lambda metadata: config)

    @graph.app.route("/ok")
    @graph.audit
    @graph.basic_auth.required
    def unauthorized():
        return "OK"

    client = graph.app.test_client()

    response = client.get("/ok", headers={
        "Authorization": encode_basic_auth("username", "password"),
    })
    assert_that(response.status_code, is_(equal_to(200)))
