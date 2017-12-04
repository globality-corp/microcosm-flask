"""
Conventions for CSV-returning CRUD endpoints.

"""
from functools import wraps
from inflection import pluralize

from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.encoding import (
    dump_response_data,
    merge_data,
)
from microcosm_flask.conventions.registry import qs, response
from microcosm_flask.operations import Operation
from microcosm_flask.paging import identity, OffsetLimitPage, OffsetLimitPageSchema


class CSVConvention(Convention):

    @property
    def content_type(self):
        return "text/csv"

    @property
    def page_cls(self):
        return OffsetLimitPage

    @property
    def page_schema(self):
        return OffsetLimitPageSchema

    def configure_search(self, ns, definition):
        """
        Register a search endpoint.

        The definition's func should be a search function, which must:
        - accept kwargs for the query string (minimally for pagination)
        - return a tuple of (items, count) where count is the total number of items
          available (in the case of pagination)

        The definition's request_schema will be used to process query string arguments.

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        paginated_list_schema = self.page_cls.make_paginated_list_schema_class(
            ns,
            definition.response_schema,
        )()

        @self.add_route(ns.collection_path, Operation.Search, ns)
        @qs(definition.request_schema)
        @response(self.content_type)
        @wraps(definition.func)
        def search(**path_data):
            page = self.page_cls.from_query_string(definition.request_schema)
            result = definition.func(**merge_data(path_data, page.to_dict(func=identity)))
            response_data, headers = page.to_paginated_list(result, ns, Operation.Search)
            definition.header_func(headers)
            return dump_response_data(paginated_list_schema, response_data, headers=headers, response_format="csv")

        search.__doc__ = "Search the collection of all {}".format(pluralize(ns.subject_name))


def configure_csv(graph, ns, mappings):
    """
    Register CSV-returning endpoints for a resource object.

    :param mappings: a dictionary from operations to tuple, where each tuple contains
                     the target function and zero or more marshmallow schemas according
                     to the signature of the "register_<foo>_endpoint" functions

    Example mapping:

        {
            Operation.Create: (create_foo, NewFooSchema(), FooSchema()),
            Operation.Delete: (delete_foo,),
            Operation.Retrieve: (retrieve_foo, FooSchema()),
        }

    """
    convention = CSVConvention(graph)
    convention.configure(ns, mappings)
