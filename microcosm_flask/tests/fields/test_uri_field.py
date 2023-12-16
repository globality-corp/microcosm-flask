"""
Test URI field.

"""
import pytest
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    is_,
    raises,
)
from marshmallow import Schema, ValidationError

from microcosm_flask.fields import URIField
from microcosm_flask.fields.uri_field import normalize_uri


class URISchema(Schema):
    foo = URIField(include_query=True)


@pytest.mark.parametrize(
    "uri, expected",
    [
        ("http://example.com", "http://example.com"),
        ("http://example.com/", "http://example.com"),
        ("http://example.com//", "http://example.com"),
        ("http://example.com/foo/", "http://example.com/foo"),
        (
            "http://username:password@example.com",
            "http://username:password@example.com",
        ),
        ("http://ExAmPlE.com", "http://example.com"),
        ("http://example.com:80", "http://example.com"),
        ("http://example.com:8080", "http://example.com:8080"),
        ("http://example.com/Foo#Bar", "http://example.com/Foo#Bar"),
        ("http://example.com/?foo=bar&bar=baz", "http://example.com?bar=baz&foo=bar"),
    ],
)
def test_normalize_uri(uri, expected):
    assert_that(normalize_uri(uri), is_(equal_to(expected)))


def test_uri_dump():
    schema = URISchema()
    result = schema.dump(
        dict(
            foo="http://example.com",
        )
    )
    assert_that(result["foo"], is_(equal_to("http://example.com")))


def test_uri_dump_malformed():
    schema = URISchema()
    assert_that(
        calling(schema.dump).with_args(
            dict(
                foo="example",
            ),
        ),
        raises(ValidationError),
    )


def test_uri_load():
    schema = URISchema()
    result = schema.load(
        dict(
            foo="http://example.com",
        )
    )
    assert_that(result["foo"], is_(equal_to("http://example.com")))


def test_uri_load_malformed():
    schema = URISchema()
    assert_that(
        calling(schema.load).with_args(
            dict(
                foo="example",
            ),
        ),
        raises(ValidationError),
    )
