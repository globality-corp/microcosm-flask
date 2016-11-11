"""
Pagination support.

"""
from enum import Enum

from marshmallow import fields, Schema

from microcosm_flask.linking import Link, Links
from microcosm_flask.operations import Operation


class PageSchema(Schema):
    offset = fields.Integer(missing=0, default=0)
    limit = fields.Integer(missing=20, limit=20)


def make_paginated_list_schema(ns, item_schema):
    """
    Generate a paginated list schema.

    :param ns: a `Namespace` for the list's item type
    :param item_schema: a `Schema` for the list's item type

    """

    class PaginatedListSchema(Schema):
        __alias__ = "{}_list".format(ns.subject_name)

        offset = fields.Integer(required=True)
        limit = fields.Integer(required=True)
        count = fields.Integer(required=True)
        items = fields.List(fields.Nested(item_schema), required=True)
        _links = fields.Raw()

    return PaginatedListSchema


class Page(object):

    def __init__(self, offset, limit, **rest):
        self.offset = offset
        self.limit = limit
        self.rest = rest

    @classmethod
    def from_query_string(cls, qs):
        """
        Create a page from a query string dictionary.

        This dictionary should probably come from `PageSchema.from_request()`.

        """
        dct = qs.copy()
        offset = dct.pop("offset", None)
        limit = dct.pop("limit", None)
        return cls(
            offset=offset,
            limit=limit,
            **dct
        )

    def next(self):
        return Page(
            offset=self.offset + self.limit,
            limit=self.limit,
            **self.rest
        )

    def prev(self):
        return Page(
            offset=self.offset - self.limit,
            limit=self.limit,
            **self.rest
        )

    def to_dict(self):
        return dict(self.to_tuples())

    def to_tuples(self):
        """
        Convert to tuples for deterministic order when passed to urlencode.

        """
        return [
            ("offset", self.offset),
            ("limit", self.limit),
        ] + [
            (key, self._qs_value_for_tuple(self.rest[key]))
            for key in sorted(self.rest.keys())
        ]

    def _qs_value_for_tuple(self, value):
        if isinstance(value, Enum):
            return value.name
        return value


class PaginatedList(object):

    def __init__(self,
                 ns,
                 page,
                 items,
                 count,
                 schema=None,
                 operation=Operation.Search,
                 **extra):
        self.ns = ns
        self.page = page
        self.items = items
        self.count = count
        self.schema = schema
        self.operation = operation
        self.extra = extra

    def to_dict(self):
        return dict(
            count=self.count,
            items=[
                self.schema.dump(item).data if self.schema else item
                for item in self.items
            ],
            _links=self._links,
            **self.page.to_dict()
        )

    @property
    def offset(self):
        return self.page.offset

    @property
    def limit(self):
        return self.page.limit

    @property
    def _links(self):
        return self.links.to_dict()

    @property
    def links(self):
        links = Links()
        links["self"] = Link.for_(self.operation, self.ns, qs=self.page.to_tuples(), **self.extra)
        if self.page.offset + self.page.limit < self.count:
            links["next"] = Link.for_(self.operation, self.ns, qs=self.page.next().to_tuples(), **self.extra)
        if self.page.offset > 0:
            links["prev"] = Link.for_(self.operation, self.ns, qs=self.page.prev().to_tuples(), **self.extra)
        return links
