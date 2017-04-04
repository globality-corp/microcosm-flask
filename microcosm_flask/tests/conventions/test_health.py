"""
Health check convention tests.

"""
from json import loads

from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm.api import create_object_graph


def test_health_check():
    """
    Default health check returns OK.

    """
    graph = create_object_graph(name="example", testing=True)
    graph.use("health_convention")

    client = graph.flask.test_client()

    response = client.get("/api/health")
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to({
        "name": "example",
        "ok": True,
    })))


def test_health_check_custom_check():
    """
    Should return Custom health check results.

    """
    graph = create_object_graph(name="example", testing=True)
    graph.use("health_convention")

    client = graph.flask.test_client()

    graph.health_convention.checks["foo"] = lambda graph: "hi"

    response = client.get("/api/health")
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to({
        "name": "example",
        "ok": True,
        "checks": {
            "foo": {
                "message": "hi",
                "ok": True,
            },
        },
    })))


def test_health_check_custom_check_failed():
    """
    Should return 503 on health check failure.

    """
    graph = create_object_graph(name="example", testing=True)
    graph.use("health_convention")

    client = graph.flask.test_client()

    def fail(graph):
        raise Exception("failure!")

    graph.health_convention.checks["foo"] = fail

    response = client.get("/api/health")
    assert_that(response.status_code, is_(equal_to(503)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to({
        "name": "example",
        "ok": False,
        "checks": {
            "foo": {
                "message": "failure!",
                "ok": False,
            },
        },
    })))
