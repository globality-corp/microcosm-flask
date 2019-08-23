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


class TestEnum(Enum):
    A = "A"
    B = "B"


class EnumQueryStringListSchema(Schema):
    foo_ids = QueryStringList(EnumField(TestEnum))


def test_query_list_deserialize_items():
    schema = EnumQueryStringListSchema()
    result = schema.load(
        ImmutableMultiDict([("foo_ids", "A,B")]),
    )

    assert_that(result["foo_ids"], is_(equal_to([TestEnum.A, TestEnum.B])))


def test_query_list_load_with_comma_separated_single_keys():
    """
    tests for support of /foo?foo_ids=1,2
    """
    schema = QueryStringListSchema()
    result = schema.load(
        ImmutableMultiDict([("foo_ids", "a,b")]),
    )

    assert_that(result["foo_ids"], is_(equal_to(["a", "b"])))


def test_query_list_load_with_duplicate_keys():
    """
    tests for support of /foo?foo_ids[]=1&foo_ids[]=2
    """
    schema = QueryStringListSchema()
    result = schema.load(
        ImmutableMultiDict([("foo_ids", "a"), ("foo_ids", "b")]),
    )

    assert_that(result["foo_ids"], is_(equal_to(["a", "b"])))


def test_query_list_dump():
    schema = QueryStringListSchema()
    result = schema.dump({
        "foo_ids": ["a"],
    })

    assert_that(result["foo_ids"], is_(equal_to(["a"])))
