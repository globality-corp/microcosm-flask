"""
Test json formatting.

"""
from hamcrest import assert_that, contains_inanyorder, equal_to, is_
from microcosm.api import create_object_graph

from microcosm_flask.formatting import JSONFormatter
from microcosm_flask.tests.formatting.base import etag_for


def test_make_response():
    graph = create_object_graph(name="example", testing=True)
    formatter = JSONFormatter()

    with graph.app.test_request_context():
        response = formatter(dict(foo="bar"))

    assert_that(response.data, is_(equal_to(b'{"foo":"bar"}\n')))
    assert_that(response.content_type, is_(equal_to("application/json")))
    assert_that(response.headers, contains_inanyorder(
        ("Content-Type", "application/json"),
        ("Content-Length", "14"),
        ("ETag", etag_for(
            md5_hash='"2f8acf3fe5e5c2839a04b7677d9399b8"',
            spooky_hash='"af072b51e1eb2a8d7b2ab84dab972674"',
        )),
    ))
