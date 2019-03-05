"""
Test context.

"""
from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph


def test_request_context():
    graph = create_object_graph(name="example", testing=True)
    graph.use(
        "opaque",
        "request_context",
    )

    with graph.flask.test_request_context(headers={
            "X-Request-Id": "foo",
    }):
        with graph.opaque.initialize(graph.request_context):
            assert_that(graph.opaque["X-Request-Id"], is_(equal_to("foo")))
