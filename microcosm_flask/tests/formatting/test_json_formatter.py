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
from microcosm_flask.tests.formatting.base import etag_for


def test_make_response():
    graph = create_object_graph(name="example", testing=True)
    formatter = JSONFormatter()

    with graph.app.test_request_context():
        response = formatter(dict(foo="bar"))

    assert_that(response.data, is_(equal_to(b'{"foo":"bar"}\n')))
    assert_that(response.content_type, is_(equal_to("application/json")))
    print("hello", response.headers)
    assert_that(response.headers, contains_inanyorder(
        ("Content-Type", "application/json"),
        ("Content-Length", "14"),
        ("ETag", etag_for(
            sha1_hash='"15abb9bce7cf6dc65ab2f6bc6aebfd406448434b"',
            spooky_hash='"053dd24aa81b8b2c3243143a14834d37"',
        )),
    ))
