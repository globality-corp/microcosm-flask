"""
Test query string list.

"""
from enum import Enum

from hamcrest import assert_that, equal_to, is_
from marshmallow import Schema
from marshmallow.fields import String
from werkzeug.datastructures import ImmutableMultiDict

from microcosm_flask.fields import EnumField, QueryStringList


class QueryStringListSchema(Schema):
    foo_ids = QueryStringList(String())


class NullableQueryStringListSchema(Schema):
    foo_ids = QueryStringList(String(), allow_none=True)


class ForTestEnum(Enum):
    A = "A"
    B = "B"


class EnumQueryStringListSchema(Schema):
    foo_ids = QueryStringList(EnumField(ForTestEnum))


def test_query_list_deserialize_items():
    schema = EnumQueryStringListSchema()
    result = schema.load(
        ImmutableMultiDict([("foo_ids", "A,B")]),
    )

    assert_that(result["foo_ids"], is_(equal_to([ForTestEnum.A, ForTestEnum.B])))


def test_query_list_load_with_comma_separated_single_keys():
    """
    tests for support of /foo?foo_ids=a,b
    """
    schema = QueryStringListSchema()
    result = schema.load(
        ImmutableMultiDict([("foo_ids", "a,b")]),
    )

    assert_that(result["foo_ids"], is_(equal_to(["a", "b"])))


def test_query_list_load_with_duplicate_keys():
    """
    tests for support of /foo?foo_ids[]=a&foo_ids[]=b
    """
    schema = QueryStringListSchema()
    result = schema.load(
        ImmutableMultiDict([("foo_ids", "a"), ("foo_ids", "b")]),
    )

    assert_that(result["foo_ids"], is_(equal_to(["a", "b"])))


def test_empty_query_list_load():
    """
    tests for support of /foo?foo_ids=&bar=...
    """
    schema = QueryStringListSchema()
    result = schema.load(
        ImmutableMultiDict([("foo_ids", "")]),
    )

    assert_that(result["foo_ids"], is_(equal_to([])))


def test_none_query_list_load():
    """
    tests for support of /foo?foo_ids=&bar=...
    """
    schema = NullableQueryStringListSchema()
    result = schema.load(
        ImmutableMultiDict([("foo_ids", None)]),
    )

    assert_that(result["foo_ids"], is_(equal_to(None)))


def test_query_list_dump():
    schema = QueryStringListSchema()
    result = schema.dump(
        {
            "foo_ids": ["a"],
        }
    )

    assert_that(result["foo_ids"], is_(equal_to(["a"])))
