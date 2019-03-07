"""
Landing convention tests.

"""
from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph


def test_landing():
    """
    Default landing returns OK.

    """
    graph = create_object_graph(name="example", testing=True)
    graph.use("landing_convention")

    client = graph.flask.test_client()

    response = client.get("/")
    assert_that(response.status_code, is_(equal_to(200)))
