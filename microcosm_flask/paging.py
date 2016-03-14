"""
Pagination support.

"""
from marshmallow import fields, Schema

from microcosm_flask.linking import Link, Links
from microcosm_flask.naming import name_for
from microcosm_flask.operations import Operation


class PageSchema(Schema):
    offset = fields.Integer(missing=0, default=0)
    limit = fields.Integer(missing=20, limit=20)


def make_paginated_list_schema(obj, obj_schema):
    """
    Generate a paginated list schema.

    """

    class PaginatedListSchema(Schema):
        __alias__ = "{}_list".format(name_for(obj))

        offset = fields.Integer(required=True)
        limit = fields.Integer(required=True)
        count = fields.Integer(required=True)
        items = fields.List(fields.Nested(obj_schema), required=True)
        links = fields.Raw(dump_to="_links")

    return PaginatedListSchema


class Page(object):
    def __init__(self, offset, limit):
        self.offset = offset
        self.limit = limit

    @classmethod
    def from_query_string(cls, qs):
        """
        Create a page from a query string dictionary.

        This dictionary should probably come from `PageSchema.from_request()`.

        """
        return cls(
            offset=qs["offset"],
            limit=qs["limit"],
        )

    def next(self):
        return Page(
            offset=self.offset + self.limit,
            limit=self.limit,
        )

    def prev(self):
        return Page(
            offset=self.offset - self.limit,
            limit=self.limit,
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
        ]


class PaginatedList(object):

    def __init__(self,
                 obj,
                 page,
                 items,
                 count,
                 schema=None,
                 operation=Operation.Search,
                 **extra):
        self.obj = obj
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
            _links=self.links.to_dict(),
            **self.page.to_dict()
        )

    @property
    def links(self):
        links = Links()
        links["self"] = Link.for_(self.operation, self.obj, qs=self.page.to_tuples(), **self.extra)
        if self.page.offset + self.page.limit < self.count:
            links["next"] = Link.for_(self.operation, self.obj, qs=self.page.next().to_tuples(), **self.extra)
        if self.page.offset > 0:
            links["prev"] = Link.for_(self.operation, self.obj, qs=self.page.prev().to_tuples(), **self.extra)
        return links
