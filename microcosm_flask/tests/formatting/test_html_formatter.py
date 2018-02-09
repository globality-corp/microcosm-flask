"""
Test html formatting.

"""
from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    is_,
)

from microcosm_flask.formatting import HTMLFormatter
from microcosm_flask.tests.formatting.base import etag_for


def test_make_response():
    formatter = HTMLFormatter()

    response = formatter("<blink>Hello World!</blink>")
    assert_that(response.data, is_(equal_to(b"<blink>Hello World!</blink>")))
    assert_that(response.content_type, is_(equal_to("text/html; charset=utf-8")))
    assert_that(response.headers, contains_inanyorder(
        ("Content-Length", "27"),
        ("Content-Type", "text/html; charset=utf-8"),
        ("ETag", etag_for(
            md5_hash='"016a5a134aceb7391754f03893d30e06"',
            spooky_hash='"1a639cef905e11904ac33817c37997dd"',
        )),
    ))
