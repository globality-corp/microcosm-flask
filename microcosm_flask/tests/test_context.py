"""
Test context.

"""
from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph

from microcosm_flask.context import get_request_context


def test_request_context():
    graph = create_object_graph(name="example", testing=True)
    graph.use(
        "opaque",
    )

    with graph.flask.test_request_context(headers={
            "X-Request-Id": "foo",
    }):
        with graph.opaque.initialize(get_request_context):
            assert_that(graph.opaque["X-Request-Id"], is_(equal_to("foo")))
