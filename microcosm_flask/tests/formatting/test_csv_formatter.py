"""
Test CSV formatting.

"""
from codecs import BOM_UTF8

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

    assert_that(response.data, is_(equal_to(BOM_UTF8 + b"foo\r\nbar\r\nbaz\r\n")))
    assert_that(response.content_type, is_(equal_to("text/csv; charset=utf-8")))
    assert_that(response.headers, contains_inanyorder(
        ("Content-Disposition", "attachment; filename=\"response.csv\""),
        ("Content-Type", "text/csv; charset=utf-8"),
        ("ETag", etag_for(
            sha1_hash='"a1ce622dcb1bcf03565e4d6925adb1e752d86080"',
            spooky_hash='"e264d2b6b13c5298cb2059716018aa4d"',
        )),
    ))


def test_make_response_tuples():
    formatter = CSVFormatter()

    response = formatter(dict(items=[
        ("a", "b", "c"),
        ("d", "e", "f"),
    ]))

    assert_that(response.data, is_(equal_to(BOM_UTF8 + b"a,b,c\r\nd,e,f\r\n")))
    assert_that(response.content_type, is_(equal_to("text/csv; charset=utf-8")))
    assert_that(response.headers, contains_inanyorder(
        ("Content-Disposition", "attachment; filename=\"response.csv\""),
        ("Content-Type", "text/csv; charset=utf-8"),
        ("ETag", etag_for(
            sha1_hash='"e4020b884f3ea6fe2bdd18dbf50495bcc32bb430"',
            spooky_hash='"37cd063df88efefe1929f3cf4532b718"',
        )),
    ))


def test_make_response_list():
    formatter = CSVFormatter()

    response = formatter(dict(items=[
        ["a", "b", "c"],
        ["d", "e", "f"],
    ]))

    assert_that(response.data, is_(equal_to(BOM_UTF8 + b"a,b,c\r\nd,e,f\r\n")))
    assert_that(response.content_type, is_(equal_to("text/csv; charset=utf-8")))
    assert_that(response.headers, contains_inanyorder(
        ("Content-Disposition", "attachment; filename=\"response.csv\""),
        ("Content-Type", "text/csv; charset=utf-8"),
        ("ETag", etag_for(
            sha1_hash='"e4020b884f3ea6fe2bdd18dbf50495bcc32bb430"',
            spooky_hash='"37cd063df88efefe1929f3cf4532b718"',
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

    assert_that(response.data, is_(equal_to(BOM_UTF8 + b"id,firstName,lastName\r\nme,First,Last\r\n")))
    assert_that(response.content_type, is_(equal_to("text/csv; charset=utf-8")))
    assert_that(response.headers, contains_inanyorder(
        ("Content-Disposition", "attachment; filename=\"response.csv\""),
        ("Content-Type", "text/csv; charset=utf-8"),
        ("ETag", etag_for(
            sha1_hash='"9f2b4c62a05e78d0417a92741321f03e3382cb56"',
            spooky_hash='"994df8aa1632af103265ebeae37a3804"',
        )),
    ))
