"""
Logging level test convention.

"""
from json import dumps, loads
from time import time

from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    has_items,
    is_,
)
from microcosm.api import create_object_graph
from mock import patch

from microcosm_flask.conventions.logging_level import UntilDeadline


def test_retrieve_logging_levels():
    """
    Default health check returns OK.

    """
    graph = create_object_graph(name="example", testing=True)
    graph.use("logging_level_convention")
    graph.lock()

    client = graph.flask.test_client()

    response = client.get("/api/logging_level")
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(
        data,
        # this is a partial match
        has_entries(
            name="",
            level="INFO",
            children=has_items(
                has_entries(
                    name="bravado",
                    level="INFO",
                    children=has_items(
                        has_entries(
                            name="bravado.requests_client",
                            level="ERROR",
                        ),
                    ),
                ),
                has_entries(
                    name="requests",
                    level="WARNING",
                ),
            ),
        ),
    )


def test_create_conditional_logging_level():
    """
    Default health check returns OK.

    """
    graph = create_object_graph(name="example", testing=True)
    graph.use("logging_level_convention")
    graph.lock()

    client = graph.flask.test_client()

    response = client.patch("/api/logging_level", data=dumps(dict(
        duration=1.0,
        name="requests",
    )))
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(
        data,
        # this is a partial match
        has_entries(
            children=has_items(
                has_entries(
                    name="requests",
                    level="DEBUG",
                ),
            ),
        ),
    )

    with patch.object(UntilDeadline, "now") as mocked:
        mocked.return_value = time() + 2

        response = client.patch("/api/logging_level", data=dumps(dict(
            duration=1.0,
            name="requests",
        )))

    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(
        data,
        # this is a partial match
        has_entries(
            children=has_items(
                has_entries(
                    name="requests",
                    level="DEBUG",
                ),
            ),
        ),
    )
