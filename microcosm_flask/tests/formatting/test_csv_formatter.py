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
            sha1_hash='"959fa0271c7e205c28d778030661eb8e608e6c10"',
            spooky_hash='"02dee263db4f9326a3fbee9135939717"',
        )),
    ))


def test_make_response_tuples():
    formatter = CSVFormatter()

    response = formatter(dict(items=[
        ("a", "b", "c"),
        ("d", "e", "f"),
    ]))

    assert_that(response.data, is_(equal_to(b"a,b,c\r\nd,e,f\r\n")))
    assert_that(response.content_type, is_(equal_to("text/csv; charset=utf-8")))
    assert_that(response.headers, contains_inanyorder(
        ("Content-Disposition", "attachment; filename=\"response.csv\""),
        ("Content-Type", "text/csv; charset=utf-8"),
        ("ETag", etag_for(
            sha1_hash='"968dd638d0cf781bdff97e5c44c8cc34915600c1"',
            spooky_hash='"63b989eb36315937ef68206fb9fc3104"',
        )),
    ))


def test_make_response_list():
    formatter = CSVFormatter()

    response = formatter(dict(items=[
        ["a", "b", "c"],
        ["d", "e", "f"],
    ]))

    assert_that(response.data, is_(equal_to(b"a,b,c\r\nd,e,f\r\n")))
    assert_that(response.content_type, is_(equal_to("text/csv; charset=utf-8")))
    assert_that(response.headers, contains_inanyorder(
        ("Content-Disposition", "attachment; filename=\"response.csv\""),
        ("Content-Type", "text/csv; charset=utf-8"),
        ("ETag", etag_for(
            sha1_hash='"968dd638d0cf781bdff97e5c44c8cc34915600c1"',
            spooky_hash='"63b989eb36315937ef68206fb9fc3104"',
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
            sha1_hash='"2b89c86c79efb72d290983d7b6406da43da65a06"',
            spooky_hash='"0a7f40b47efb0a197b180444c4911b17"',
        )),
    ))
