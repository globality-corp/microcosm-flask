"""
Health check convention tests.

"""
from unittest.mock import patch

import pytest
from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict


def test_health_check():
    """
    Default health check returns OK.

    """
    graph = create_object_graph(name="example", testing=True)
    graph.use("health_convention")

    client = graph.flask.test_client()

    graph.health_convention.optional_checks["foo"] = _health_check()

    response = client.get("/api/health")
    assert_that(response.status_code, is_(equal_to(200)))
    assert_that(
        response.json,
        is_(
            equal_to(
                {
                    "name": "example",
                    "ok": True,
                    "checks": {
                        "build_num": {"message": "undefined", "ok": True},
                        "sha1": {"message": "undefined", "ok": True},
                    },
                }
            )
        ),
    )


def test_health_check_required_check_failed():
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

    graph.health_convention.checks["foo"] = _health_check(False)

    response = client.get("/api/health")

    assert_that(response.status_code, is_(equal_to(503)))
    assert_that(
        response.json,
        is_(
            equal_to(
                {
                    "name": "example",
                    "ok": False,
                    "checks": {
                        "foo": {
                            "message": "failure!",
                            "ok": False,
                        },
                    },
                }
            )
        ),
    )


def test_health_check_required_check_failed_logging():
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
    with patch.object(graph.health_convention, "logger") as logger:
        graph.health_convention.checks["foo"] = _health_check(False)

        response = client.get("/api/health")

        assert_that(response.status_code, is_(equal_to(503)))
        assert_that(
            response.json,
            is_(
                equal_to(
                    {
                        "name": "example",
                        "ok": False,
                        "checks": {
                            "foo": {
                                "message": "failure!",
                                "ok": False,
                            },
                        },
                    }
                )
            ),
        )
        logger.exception.assert_called_once_with("Exception in health check")


def test_health_check_optional_check_failed():
    """
    Optional checks should not be evaluated by default

    """
    loader = load_from_dict(
        health_convention=dict(
            include_build_info="false",
        ),
    )
    graph = create_object_graph(name="example", testing=True, loader=loader)
    graph.use("health_convention")

    client = graph.flask.test_client()

    graph.health_convention.optional_checks["foo"] = _health_check(False)

    response = client.get("/api/health")

    assert_that(response.status_code, is_(equal_to(200)))
    assert_that(
        response.json,
        is_(
            equal_to(
                {
                    "name": "example",
                    "ok": True,
                }
            )
        ),
    )


def test_health_check_with_build_info():
    graph = create_object_graph(name="example", testing=True)
    graph.use("health_convention")

    client = graph.flask.test_client()

    response = client.get("/api/health", query_string=dict(full=True))
    assert_that(response.status_code, is_(equal_to(200)))
    assert_that(
        response.json,
        is_(
            equal_to(
                dict(
                    name="example",
                    ok=True,
                    checks=dict(
                        build_num=dict(
                            message="undefined",
                            ok=True,
                        ),
                        sha1=dict(
                            message="undefined",
                            ok=True,
                        ),
                    ),
                )
            )
        ),
    )


@pytest.mark.parametrize(
    "optional_check, full_check, expect_check_response",
    [
        # When non-optional, always end up in the response
        (False, False, True),
        (False, True, True),
        # Optional checks conditionally show up
        (True, False, False),
        (True, True, True),
    ]
)
def test_health_check_custom_checks(optional_check, full_check, expect_check_response):
    loader = load_from_dict(
        health_convention=dict(
            include_build_info="false",
        ),
    )
    graph = create_object_graph(name="example", testing=True, loader=loader)
    graph.use("health_convention")

    client = graph.flask.test_client()

    if optional_check:
        graph.health_convention.optional_checks["foo"] = _health_check()
    else:
        graph.health_convention.checks["foo"] = _health_check()

    response = client.get("/api/health", query_string=dict(full=full_check))
    assert_that(response.status_code, is_(equal_to(200)))

    expected_response = {
        "name": "example",
        "ok": True,
    }
    if expect_check_response:
        expected_response.update(
            {
                "checks": {
                    "foo": {
                        "message": "hi",
                        "ok": True,
                    },
                },
            }
        )

    assert_that(response.json, is_(equal_to(expected_response)))


@pytest.mark.parametrize(
    "optional_check, full_check, expect_failure",
    [
        # When non-optional, always end up in the response and fail
        (False, False, True),
        (False, True, True),
        # Optional checks conditionally show up, and only fail is specified
        (True, False, False),
        (True, True, True),
    ]
)
def test_health_check_custom_check_failed(optional_check, full_check, expect_failure):
    loader = load_from_dict(
        health_convention=dict(
            include_build_info="false",
        ),
    )
    graph = create_object_graph(name="example", testing=True, loader=loader)
    graph.use("health_convention")

    client = graph.flask.test_client()

    if optional_check:
        graph.health_convention.optional_checks["foo"] = _health_check(False)
    else:
        graph.health_convention.checks["foo"] = _health_check(False)

    response = client.get("/api/health", query_string=dict(full=full_check))

    if expect_failure:
        assert_that(response.status_code, is_(equal_to(503)))
        assert_that(
            response.json,
            is_(
                equal_to(
                    {
                        "name": "example",
                        "ok": False,
                        "checks": {
                            "foo": {
                                "message": "failure!",
                                "ok": False,
                            },
                        },
                    }
                )
            ),
        )
    else:
        assert_that(response.status_code, is_(equal_to(200)))
        assert_that(
            response.json,
            is_(
                equal_to(
                    {
                        "name": "example",
                        "ok": True,
                    }
                )
            ),
        )


def _health_check(success=True):
    if success:
        return lambda graph: "hi"

    def fail(graph):
        raise Exception("failure!")

    return fail
