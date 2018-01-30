"""
Test json formatting.

"""
from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    is_,
)

from microcosm.api import create_object_graph

from microcosm_flask.formatting import JSONFormatter


def test_make_response():
    graph = create_object_graph(name="example", testing=True)
    formatter = JSONFormatter()

    with graph.app.test_request_context():
        response = formatter(dict(foo="bar"))

    assert_that(response.data, is_(equal_to(b'{\n  "foo": "bar"\n}\n')))
    assert_that(response.content_type, is_(equal_to("application/json")))
    assert_that(response.headers, contains_inanyorder(
        ("Content-Type", "application/json"),
    ))
