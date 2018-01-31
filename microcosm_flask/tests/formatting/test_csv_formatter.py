"""
Test CSV formatting.

"""
from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    is_,
)

from microcosm_flask.formatting import CSVFormatter
from microcosm_flask.tests.conventions.fixtures import PersonCSVSchema
from microcosm_flask.tests.formatting.base import etag_for


def test_make_response():
    formatter = CSVFormatter()

    response = formatter(dict(items=[
        dict(foo="bar"),
        dict(foo="baz"),
    ]))

    assert_that(response.data, is_(equal_to(b"foo\r\nbar\r\nbaz\r\n")))
    assert_that(response.content_type, is_(equal_to("text/csv; charset=utf-8")))
    assert_that(response.headers, contains_inanyorder(
        ("Content-Disposition", "attachment; filename=\"response.csv\""),
        ("Content-Type", "text/csv; charset=utf-8"),
        ("ETag", etag_for(
            md5_hash='"a2ead3516dd1be4a3c7f45716c0a0eb7"',
            spooky_hash='"02dee263db4f9326a3fbee9135939717"',
        )),
    ))


def test_make_response_ordered():
    formatter = CSVFormatter(PersonCSVSchema())

    response = formatter(dict(items=[
        dict(
            firstName="First",
            lastName="Last",
            id="me",
        )
    ]))

    assert_that(response.data, is_(equal_to(b"id,firstName,lastName\r\nme,First,Last\r\n")))
    assert_that(response.content_type, is_(equal_to("text/csv; charset=utf-8")))
    assert_that(response.headers, contains_inanyorder(
        ("Content-Disposition", "attachment; filename=\"response.csv\""),
        ("Content-Type", "text/csv; charset=utf-8"),
        ("ETag", etag_for(
            md5_hash='"4480bd6748cf93740490ebeee7eae1fe"',
            spooky_hash='"0a7f40b47efb0a197b180444c4911b17"',
        )),
    ))
