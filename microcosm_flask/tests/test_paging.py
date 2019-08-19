"""
Paging tests.

"""
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_entry,
    is_,
    raises,
)
from marshmallow import Schema
from marshmallow.exceptions import ValidationError
from microcosm.api import create_object_graph

from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation
from microcosm_flask.paging import OffsetLimitPage, OffsetLimitPageSchema


def test_default_values_for_offset_limit_page():
    page = OffsetLimitPage(foo="bar")
    assert_that(page.offset, is_(equal_to(0)))
    assert_that(page.limit, is_(equal_to(20)))
    assert_that(page.kwargs, has_entry("foo", "bar"))


def test_override_default_limit_from_request_header():
    graph = create_object_graph(name="example", testing=True)
    with graph.flask.test_request_context(headers={"X-Request-Limit": "2"}):
        page = OffsetLimitPage.from_dict(dict(foo="bar"))
        assert_that(page.offset, is_(equal_to(0)))
        assert_that(page.limit, is_(equal_to(2)))
        assert_that(page.kwargs, has_entry("foo", "bar"))


def test_offset_limit_page_to_from_dict():
    page = OffsetLimitPage.from_dict(dict(offset=10, limit=10, foo="bar"))
    assert_that(page.offset, is_(equal_to(10)))
    assert_that(page.limit, is_(equal_to(10)))
    assert_that(page.to_dict(), is_(equal_to(dict(offset=10, limit=10, foo="bar"))))


def test_offset_limit_page_from_query_string():
    graph = create_object_graph(name="example", testing=True)
    with graph.flask.test_request_context(query_string="offset=1"):
        page = OffsetLimitPage.from_query_string(OffsetLimitPageSchema())
        assert_that(page.offset, is_(equal_to(1)))
        assert_that(page.limit, is_(equal_to(20)))


def test_offset_limit_page_rejects_unknown_queries():
    graph = create_object_graph(name="example", testing=True)
    with graph.flask.test_request_context(query_string="offset=1&foo=bar"):
        assert_that(
            calling(OffsetLimitPage.from_query_string).with_args(OffsetLimitPageSchema()),
            raises(ValidationError),
        )


def test_offset_limit_page_to_paginated_list():
    graph = create_object_graph(name="example", testing=True)

    ns = Namespace("foo")

    @graph.flask.route("/", methods=["GET"], endpoint="foo.search.v1")
    def search():
        pass

    with graph.flask.test_request_context():
        page = OffsetLimitPage(
            offset=10,
            limit=10,
            foo="bar",
        )
        result = [], 0
        paginated_list, headers = page.to_paginated_list(result, _ns=ns, _operation=Operation.Search)

        schema_cls = page.make_paginated_list_schema_class(ns, Schema())
        data = schema_cls().dump(paginated_list)
        assert_that(
            data,
            is_(equal_to(dict(
                offset=10,
                limit=10,
                count=0,
                items=[],
                _links=dict(
                    self=dict(
                        href="http://localhost/?offset=10&limit=10&foo=bar",
                    ),
                    prev=dict(
                        href="http://localhost/?offset=0&limit=10&foo=bar",
                    ),
                ),
            ))))
