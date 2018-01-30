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
    ))
