"""
Configuration discovery convention tests.

"""
from json import loads

from hamcrest import assert_that, equal_to, has_entries, is_
from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict
from microcosm.loaders.compose import load_config_and_secrets


def test_config_discovery():
    """
    Config-minus secrets is shareable.

    """
    config = load_from_dict(
        config_convention=dict(
            enabled="true",
        ),
    )
    secrets = load_from_dict(
        config_convention=dict(
            enabled="true",
        ),
    )
    paritioned_loader = load_config_and_secrets(config, secrets)

    graph = create_object_graph(name="example", testing=True, loader=paritioned_loader)
    graph.use("config_convention")

    client = graph.flask.test_client()

    response = client.get(
        "/api/config",
    )
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))

    assert_that(data, has_entries(config_convention=dict(enabled="true")))


def test_non_json_keys_omitted():
    class WeirdObject:
        pass

    loader = load_from_dict(
        config_convention=dict(
            enabled="true",
        ),
        weird_thing=WeirdObject(),
    )
    secrets = load_from_dict(dict())
    partitioned_loader = load_config_and_secrets(config=loader, secrets=secrets)
    graph = create_object_graph(name="example", testing=True, loader=partitioned_loader)
    graph.use("config_convention")

    client = graph.flask.test_client()

    response = client.get(
        "/api/config",
    )
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))

    assert_that(data, has_entries(config_convention=dict(enabled="true")))
    assert_that("weird_thing" not in data.keys())


def test_config_discovery_only_works_for_paritioned_loaders():
    """
    Config sharing is disabled if secrets are not labelled.

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
    )
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))

    assert_that(data, has_entries(msg="Config sharing disabled for non-partioned loader"))
