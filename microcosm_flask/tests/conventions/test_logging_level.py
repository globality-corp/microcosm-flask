"""
Logging level test convention.

"""
from json import loads

from hamcrest import assert_that, equal_to, has_entries, has_items, is_
from microcosm.api import create_object_graph


def test_retrieve_logging_levels():
    """
    Can retrieve current logging levels.

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
