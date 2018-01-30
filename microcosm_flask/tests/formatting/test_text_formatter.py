"""
Test text formatting.

"""
from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    is_,
)

from microcosm_flask.formatting import TextFormatter


def test_make_response():
    formatter = TextFormatter()

    response = formatter("Hello World!")
    assert_that(response.data, is_(equal_to(b"Hello World!")))
    assert_that(response.content_type, is_(equal_to("text/plain; charset=utf-8")))
    assert_that(response.headers, contains_inanyorder(
        ("Content-Length", "12"),
        ("Content-Type", "text/plain; charset=utf-8"),
    ))
