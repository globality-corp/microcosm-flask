"""
Test query string list.

"""
from hamcrest import (
    assert_that,
    equal_to,
    is_,
)
from werkzeug.datastructures import ImmutableMultiDict
from marshmallow import Schema
from marshmallow.fields import String

from microcosm_flask.fields import QueryStringList


class QueryStringListSchema(Schema):
    foo_ids = QueryStringList(String())


def test_query_list_load_with_comma_separated_single_keys():
    """
    tests for support of /foo?foo_ids=1,2
    """
    schema = QueryStringListSchema()
    result = schema.load(
        ImmutableMultiDict([("foo_ids", "a,b")]),
    )

    assert_that(result.data["foo_ids"], is_(equal_to(["a", "b"])))


def test_query_list_load_with_duplicate_keys():
    """
    tests for support of /foo?foo_ids[]=1&foo_ids[]=2
    """
    schema = QueryStringListSchema()
    result = schema.load(
        ImmutableMultiDict([("foo_ids", "a"), ("foo_ids", "b")]),
    )

    assert_that(result.data["foo_ids"], is_(equal_to(["a", "b"])))


def test_query_list_dump():
    schema = QueryStringListSchema()
    result = schema.dump({
        "foo_ids": ["a"],
    })

    assert_that(result.data["foo_ids"], is_(equal_to("a")))
