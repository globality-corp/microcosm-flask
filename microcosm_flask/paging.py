"""
Pagination support.

Most applications start with offset/limit pagination because it's simplest to implement,
but other pagination schemes are possible and can be more performant especially in infinite
scroll settings. This module encapsulates paging into a set of extensible, inter-related objects.

 -  A `Page` represents information about a specific page (for example, the currently requested one)
 -  A `PageSchema` defines a (marshmallow) schema for decoding a page from some data (e.g. the query string)
 -  A `PaginatedList` defines a list of items that knows about its current page and *may* define HAL-style
    links to other pages.
 -  A `PaginatedListSchema` defines a (marshmallow) schema for encoding a paginated list (e.g. in a response)


Typical Usage:

    # pre-conditions: we are processes a search operation for `foo`
    ns, operation, foo_schema = Namespace("foo"), Operation.Search, Schema()

    # choose a page implementation
    page_cls = OffsetLimitPage

    # choose a page schema (we may wish to extend the base class for more search arguments)
    page_schema = OffsetLimitPageSchema()

    # construct the current page from the query string
    page = page_cls.from_query_string(page_schema)

    # perform the search; result is typically a tuple including items and a total count
    result = some_search_func(page)

    # transform the result into a paginated list and possibly response headers
    paginated_list, headers = page.to_paginated_list(result, ns, operation)

    # encode the result
    paginated_list_schema = page_cls.make_paginated_list_schema_class(ns, foo_schema)()
    return dump_response_Data(paginated_list_schema, paginated_list, headers=headers)

"""
from flask import request
from marshmallow import Schema, fields

from microcosm_flask.conventions.encoding import encode_count_header, load_query_string_data
from microcosm_flask.linking import Link, Links


def identity(x):
    """
    Identity function.

    """
    return x


# NB: lots of code currently uses `PageSchema` to refer to `OffsetLimitPageSchema`
# keeping this (mis)naming for backwards compatibilty
class PageSchema(Schema):
    offset = fields.Integer(missing=None)
    limit = fields.Integer(missing=None)


class OffsetLimitPageSchema(PageSchema):
    pass


class PaginatedList:
    """
    A list of items with knowledge of a page.

    Includes HAL-style links (e.g for the current or next page)

    """
    def __init__(self, items, _page, _ns, _operation, _context):
        self.items = items
        self._page = _page
        self._ns = _ns
        self._operation = _operation
        self._context = _context

    @property
    def _links(self):
        return self.links.to_dict()

    @property
    def links(self):
        """
        Include a self link.

        """
        links = Links()
        links["self"] = Link.for_(
            self._operation,
            self._ns,
            qs=self._page.to_items(),
            **self._context
        )
        return links


class OffsetLimitPaginatedList(PaginatedList):
    """
    A paginated list using offset/limit style paging.

    """
    def __init__(self, items, count, _page, _ns, _operation, _context):
        super(OffsetLimitPaginatedList, self).__init__(
            items=items,
            _page=_page,
            _ns=_ns,
            _operation=_operation,
            _context=_context,
        )
        self.count = count

    @property
    def offset(self):
        return self._page.offset

    @property
    def limit(self):
        return self._page.limit

    @property
    def links(self):
        """
        Include previous and next links.

        """
        links = super(OffsetLimitPaginatedList, self).links
        if self._page.offset + self._page.limit < self.count:
            links["next"] = Link.for_(
                self._operation,
                self._ns,
                qs=self._page.next_page.to_items(),
                **self._context
            )
        if self.offset > 0:
            links["prev"] = Link.for_(
                self._operation,
                self._ns,
                qs=self._page.prev_page.to_items(),
                **self._context
            )
        return links


class Page:
    """
    Encapsulates pagination information.

    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def to_items(self, func=str):
        """
        Contruct a list of dictionary items.

        The items are normalized using:
          -  A sort function by key (for consistent results)
          -  A transformation function for values

        The transformation function will default to `str`, which is a good choice when encoding values
        as part of a response; this requires that complex types (UUID, Enum, etc.) have a valid string
        encoding.

        The transformation function should be set to `identity` in cases where raw values are desired;
        this is normally necessary when passing page data to controller functions as kwargs.

        """
        return [
            (key, func(self.kwargs[key]))
            for key in sorted(self.kwargs.keys())
        ]

    def to_dict(self, func=str):
        return dict(self.to_items(func=func))

    def to_paginated_list(self, result, _ns, _operation, **kwargs):
        """
        Convert a controller result to a paginated list.

        The result format is assumed to meet the contract of this page class's `parse_result` function.

        """
        items, context = self.parse_result(result)
        headers = dict()
        paginated_list = PaginatedList(
            items=items,
            _page=self,
            _ns=_ns,
            _operation=_operation,
            _context=context,
        )
        return paginated_list, headers

    @classmethod
    def parse_result(cls, result):
        """
        Parse a simple items result.

        May either be two item tuple containing items and a context dictionary (see: relation convention)
        or a list of items.

        """
        if isinstance(result, tuple) == 2:
            items, context = result
        else:
            context = {}
            items = result
        return items, context

    @classmethod
    def from_query_string(cls, schema, qs=None):
        """
        Extract a page from the current query string.

        :param qs: a query string dictionary (`request.args` will be used if omitted)

        """
        dct = load_query_string_data(schema, qs)
        return cls.from_dict(dct)

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)

    @classmethod
    def make_paginated_list_schema_class(cls, ns, item_schema):
        """
        Generate a schema class that represents a paginted list of items.

        """
        class PaginatedListSchema(Schema):
            __alias__ = "{}_list".format(ns.subject_name)
            items = fields.List(fields.Nested(item_schema), required=True)
            _links = fields.Raw()

        return PaginatedListSchema


class OffsetLimitPage(Page):
    """
    Offset/limit based paging.

    """
    def __init__(self, offset=None, limit=None, **kwargs):
        super(OffsetLimitPage, self).__init__(**kwargs)
        self.offset = self.default_offset if offset is None else offset
        self.limit = self.default_limit if limit is None else limit

    @property
    def next_page(self):
        return OffsetLimitPage(
            offset=self.offset + self.limit,
            limit=self.limit,
            **self.kwargs
        )

    @property
    def prev_page(self):
        return OffsetLimitPage(
            offset=self.offset - self.limit,
            limit=self.limit,
            **self.kwargs
        )

    @property
    def default_offset(self):
        return 0

    @property
    def default_limit(self):
        try:
            return int(request.headers["X-Request-Limit"])
        except Exception:
            return 20

    def to_items(self, func=str):
        return [
            ("offset", self.offset),
            ("limit", self.limit),
        ] + super(OffsetLimitPage, self).to_items(func=func)

    def to_paginated_list(self, result, _ns, _operation, **kwargs):
        items, count, context = self.parse_result(result)
        headers = encode_count_header(count)
        paginated_list = OffsetLimitPaginatedList(
            items=items,
            count=count,
            _page=self,
            _ns=_ns,
            _operation=_operation,
            _context=context,
        )
        return paginated_list, headers

    @classmethod
    def parse_result(cls, result):
        """
        Parse an items + count tuple result.

        May either be three item tuple containing items, count, and a context dictionary (see: relation convention)
        or a two item tuple containing only items and count.

        """
        if len(result) == 3:
            items, count, context = result
        else:
            context = {}
            items, count = result
        return items, count, context

    @classmethod
    def make_paginated_list_schema_class(cls, ns, item_schema):
        class PaginatedListSchema(Schema):
            __alias__ = "{}_list".format(ns.subject_name)

            offset = fields.Integer(required=True)
            limit = fields.Integer(required=True)
            count = fields.Integer(required=True)
            items = fields.List(fields.Nested(item_schema), required=True)
            _links = fields.Raw()

            @property
            def csv_column_order(self):
                return getattr(item_schema, "csv_column_order", None)

        return PaginatedListSchema
