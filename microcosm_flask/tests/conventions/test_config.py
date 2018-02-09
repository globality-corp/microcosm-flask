"""
Configuration discovery convention tests.

"""
from json import loads

from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    is_,
)

from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict
from microcosm_flask.basic_auth import encode_basic_auth


def test_config_discovery():
    """
    Default health check returns OK.

    """
    loader = load_from_dict(
        config_convention=dict(
            enabled="true",
        ),
    )
    graph = create_object_graph(name="example", testing=True, loader=loader)
    graph.use("config_convention")

    client = graph.flask.test_client()

    response = client.get(
        "/api/config",
        headers={"Authorization": encode_basic_auth("default", "secret")},
    )
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))

    assert_that(data, has_entries(config_convention=dict(enabled="true")))


def test_config_convention_disabled_by_default():
    graph = create_object_graph(name="example", testing=True)
    graph.use("config_convention")

    client = graph.flask.test_client()

    response = client.get(
        "/api/config",
        headers={"Authorization": encode_basic_auth("default", "secret")},
    )
    assert_that(response.status_code, is_(equal_to(404)))


def test_non_json_keys_omitted():
    class WeirdObject:
        pass

    loader = load_from_dict(
        config_convention=dict(
            enabled="true",
        ),
        weird_thing=WeirdObject(),
    )
    graph = create_object_graph(name="example", testing=True, loader=loader)
    graph.use("config_convention")

    client = graph.flask.test_client()

    response = client.get(
        "/api/config",
        headers={"Authorization": encode_basic_auth("default", "secret")},
    )
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))

    assert_that(data, has_entries(config_convention=dict(enabled="true")))
    assert_that("weird_thing" not in data.keys())
