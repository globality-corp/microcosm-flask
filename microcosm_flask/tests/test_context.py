"""
Test context.

"""
from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph

from microcosm_flask.context import make_get_request_context


def test_request_context():
    graph = create_object_graph(name="example", testing=True)
    graph.use(
        "opaque",
    )

    with graph.flask.test_request_context(headers={
            "X-Request-Id": "foo",
    }):
        with graph.opaque.initialize(make_get_request_context()):
            assert_that(graph.opaque["X-Request-Id"], is_(equal_to("foo")))

def test_make_get_request_context_respects_passed_headers():
    graph = create_object_graph(name="example", testing=True)
    graph.use(
        "opaque",
    )

    with graph.flask.test_request_context(headers={
            "X-Foo-Id": "foo",
            "X-Bar-Id": "bar",
    }):
        with graph.opaque.initialize(make_get_request_context(["X-Bar"])):
            assert_that(graph.opaque["X-Bar-Id"], is_(equal_to("bar")))
            assert_that(graph.opaque.get("X-Foo-Id"), is_(equal_to(None)))
