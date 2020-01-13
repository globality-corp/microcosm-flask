"""
Health check convention tests.

"""
from json import loads

from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    has_entry,
    is_,
)
from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict


def test_health_check():
    """
    Default health check returns OK.

    """
    loader = load_from_dict(
        health_convention=dict(
            include_build_info="false",
        ),
    )
    graph = create_object_graph(name="example", testing=True, loader=loader)
    graph.use("health_convention")

    client = graph.flask.test_client()

    response = client.get("/api/health")
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, has_entries("name", "example", "ok", True))


def test_health_check_with_build_info():
    graph = create_object_graph(name="example", testing=True)
    graph.use("health_convention")

    client = graph.flask.test_client()

    response = client.get("/api/health")
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(
        data,
        has_entries(
            "checks",
            dict(
                build_num=dict(
                    message="undefined",
                    ok=True,
                ),
                sha1=dict(
                    message="undefined",
                    ok=True,
                ),
            )
        )
    )


def test_health_check_custom_check():
    """
    Should return Custom health check results.

    """
    loader = load_from_dict(
        health_convention=dict(
            include_build_info="false",
        ),
    )
    graph = create_object_graph(name="example", testing=True, loader=loader)
    graph.use("health_convention")

    client = graph.flask.test_client()

    graph.health_convention.checks["foo"] = lambda graph: "hi"

    response = client.get("/api/health")
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(
        data,
        has_entries(
            "checks",
            dict(
                foo=dict(
                    message="hi",
                    ok=True
                )
            )
        )
    )


def test_health_check_custom_check_failed():
    """
    Should return 503 on health check failure.

    """
    loader = load_from_dict(
        health_convention=dict(
            include_build_info="false",
        ),
    )
    graph = create_object_graph(name="example", testing=True, loader=loader)
    graph.use("health_convention")

    client = graph.flask.test_client()

    def fail(graph):
        raise Exception("failure!")

    graph.health_convention.checks["foo"] = fail

    response = client.get("/api/health")
    assert_that(response.status_code, is_(equal_to(503)))
    data = loads(response.get_data().decode("utf-8"))

    assert_that(
        data,
        has_entries(
            "checks",
            dict(
                foo=dict(
                    message="failure!",
                    ok=False,
                ),
            )
        )
    )
