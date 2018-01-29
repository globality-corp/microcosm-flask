"""
Test enums.

"""
from hamcrest import assert_that, equal_to, is_

from microcosm_flask.enums import ResponseFormats


def test_matches():
    assert_that(
        ResponseFormats.HTML.matches(
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        ),
        is_(equal_to(True)),
    )
    assert_that(
        ResponseFormats.HTML.matches(
            "text/plain,text/html;q=0.8"
        ),
        is_(equal_to(True)),
    )
