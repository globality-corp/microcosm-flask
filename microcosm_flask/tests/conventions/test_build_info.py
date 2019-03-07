"""
Build info convention tests.

"""
from json import loads

from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict


def test_build_info():
    """
    Default build info returns dict with empty keys.

    """
    graph = create_object_graph(name="example", testing=True)
    graph.use("build_info_convention")

    client = graph.flask.test_client()

    response = client.get("/api/build_info")
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to(dict(
        build_num=None,
        sha1=None,
    ))))


def test_build_info_from_environ():
    """
    Environment variables can set build info.

    """
    loader = load_from_dict(
        build_info_convention=dict(
            build_num="1",
            sha1="b08fd4a3a685c43521a931ba63872b43ec7c6bda",
        ),
    )
    graph = create_object_graph(name="example", testing=True, loader=loader)
    graph.use("build_info_convention")

    client = graph.flask.test_client()

    response = client.get("/api/build_info")
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to(dict(
        build_num="1",
        sha1="b08fd4a3a685c43521a931ba63872b43ec7c6bda",
    ))))
