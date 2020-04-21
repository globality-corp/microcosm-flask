"""
Conventions for canonical CRUD endpoints.

"""
from functools import wraps

from inflection import pluralize
from marshmallow import Schema

from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.encoding import (
    dump_response_data,
    encode_count_header,
    encode_id_header,
    load_query_string_data,
    load_request_data,
    merge_data,
    require_response_data,
)
from microcosm_flask.conventions.registry import qs, request, response
from microcosm_flask.operations import Operation
from microcosm_flask.paging import OffsetLimitPage, OffsetLimitPageSchema, identity


class CRUDConvention(Convention):

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
        @response(paginated_list_schema)
        @wraps(definition.func)
        def search(**path_data):
            page = self.page_cls.from_query_string(definition.request_schema)
            result = definition.func(**merge_data(path_data, page.to_dict(func=identity)))
            response_data, headers = page.to_paginated_list(result, ns, Operation.Search)
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                paginated_list_schema,
                response_data,
                headers=headers,
                response_format=response_format,
            )

        search.__doc__ = "Search the collection of all {}".format(pluralize(ns.subject_name))

    def configure_count(self, ns, definition):
        """
        Register a count endpoint.

        The definition's func should be a count function, which must:
        - accept kwargs for the query string
        - return a count is the total number of items available

        The definition's request_schema will be used to process query string arguments.

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        @self.add_route(ns.collection_path, Operation.Count, ns)
        @qs(definition.request_schema)
        @wraps(definition.func)
        def count(**path_data):
            request_data = load_query_string_data(definition.request_schema)
            response_data = dict()
            count = definition.func(**merge_data(path_data, request_data))
            headers = encode_count_header(count)
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                None,
                None,
                headers=headers,
                response_format=response_format,
            )

        count.__doc__ = "Count the size of the collection of all {}".format(pluralize(ns.subject_name))

    def configure_create(self, ns, definition):
        """
        Register a create endpoint.

        The definition's func should be a create function, which must:
        - accept kwargs for the request and path data
        - return a new item

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        @self.add_route(ns.collection_path, Operation.Create, ns)
        @request(definition.request_schema)
        @response(definition.response_schema)
        @wraps(definition.func)
        def create(**path_data):
            request_data = load_request_data(definition.request_schema)
            response_data = definition.func(**merge_data(path_data, request_data))
            headers = encode_id_header(response_data)
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                definition.response_schema,
                response_data,
                status_code=Operation.Create.value.default_code,
                headers=headers,
                response_format=response_format,
            )

        create.__doc__ = "Create a new {}".format(ns.subject_name)

    def configure_updatebatch(self, ns, definition):
        """
        Register an update batch endpoint.

        The definition's func should be an update function, which must:
        - accept kwargs for the request and path data
        - return a new item

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        operation = Operation.UpdateBatch

        @self.add_route(ns.collection_path, operation, ns)
        @request(definition.request_schema)
        @response(definition.response_schema)
        @wraps(definition.func)
        def update_batch(**path_data):
            headers = dict()
            request_data = load_request_data(definition.request_schema)
            response_data = definition.func(**merge_data(path_data, request_data))
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                definition.response_schema,
                response_data,
                status_code=operation.value.default_code,
                headers=headers,
                response_format=response_format,
            )

        update_batch.__doc__ = "Update a batch of {}".format(ns.subject_name)

    def configure_deletebatch(self, ns, definition):
        """
        Register a delete batch endpoint.

        The definition's func should be a delete function, which must:
        - accept kwargs for path data
        - return truthy/falsey

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        operation = Operation.DeleteBatch
        request_schema = definition.request_schema or Schema()

        @self.add_route(ns.collection_path, operation, ns)
        @qs(request_schema)
        @wraps(definition.func)
        def delete_batch(**path_data):
            headers = dict()
            request_data = load_query_string_data(request_schema)
            response_data = require_response_data(definition.func(**merge_data(path_data, request_data)))
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                response_schema="",
                response_data=None,
                status_code=operation.value.default_code,
                headers=headers,
                response_format=response_format,
            )

        delete_batch.__doc__ = "Delete a batch of {}".format(ns.subject_name)

    def configure_retrieve(self, ns, definition):
        """
        Register a retrieve endpoint.

        The definition's func should be a retrieve function, which must:
        - accept kwargs for path data
        - return an item or falsey

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        request_schema = definition.request_schema or Schema()

        @self.add_route(ns.instance_path, Operation.Retrieve, ns)
        @qs(request_schema)
        @response(definition.response_schema)
        @wraps(definition.func)
        def retrieve(**path_data):
            headers = dict()
            request_data = load_query_string_data(request_schema)
            response_data = require_response_data(definition.func(**merge_data(path_data, request_data)))
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                definition.response_schema,
                response_data,
                headers=headers,
                response_format=response_format,
            )

        retrieve.__doc__ = "Retrieve a {} by id".format(ns.subject_name)

    def configure_delete(self, ns, definition):
        """
        Register a delete endpoint.

        The definition's func should be a delete function, which must:
        - accept kwargs for path data
        - return truthy/falsey

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        request_schema = definition.request_schema or Schema()

        @self.add_route(ns.instance_path, Operation.Delete, ns)
        @qs(request_schema)
        @wraps(definition.func)
        def delete(**path_data):
            headers = dict()
            request_data = load_query_string_data(request_schema)
            response_data = require_response_data(definition.func(**merge_data(path_data, request_data)))
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                "",
                None,
                status_code=Operation.Delete.value.default_code,
                headers=headers,
                response_format=response_format,
            )

        delete.__doc__ = "Delete a {} by id".format(ns.subject_name)

    def configure_replace(self, ns, definition):
        """
        Register a replace endpoint.

        The definition's func should be a replace function, which must:
        - accept kwargs for the request and path data
        - return the replaced item

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        @self.add_route(ns.instance_path, Operation.Replace, ns)
        @request(definition.request_schema)
        @response(definition.response_schema)
        @wraps(definition.func)
        def replace(**path_data):
            headers = dict()
            request_data = load_request_data(definition.request_schema)
            # Replace/put should create a resource if not already present, but we do not
            # enforce these semantics at the HTTP layer. If `func` returns falsey, we
            # will raise a 404.
            response_data = require_response_data(definition.func(**merge_data(path_data, request_data)))
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                definition.response_schema,
                response_data,
                headers=headers,
                response_format=response_format,
            )

        replace.__doc__ = "Create or update a {} by id".format(ns.subject_name)

    def configure_update(self, ns, definition):
        """
        Register an update endpoint.

        The definition's func should be an update function, which must:
        - accept kwargs for the request and path data
        - return an updated item

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        @self.add_route(ns.instance_path, Operation.Update, ns)
        @request(definition.request_schema)
        @response(definition.response_schema)
        @wraps(definition.func)
        def update(**path_data):
            headers = dict()
            request_data = load_request_data(definition.request_schema)
            response_data = require_response_data(definition.func(**merge_data(path_data, request_data)))
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                definition.response_schema,
                response_data,
                headers=headers,
                response_format=response_format,
            )

        update.__doc__ = "Update some or all of a {} by id".format(ns.subject_name)

    def configure_createcollection(self, ns, definition):
        """
        Register create collection endpoint.

        :param ns: the namespace
        :param definition: the endpoint definition
        """
        paginated_list_schema = self.page_cls.make_paginated_list_schema_class(
            ns,
            definition.response_schema,
        )()

        @self.add_route(ns.collection_path, Operation.CreateCollection, ns)
        @request(definition.request_schema)
        @response(paginated_list_schema)
        @wraps(definition.func)
        def create_collection(**path_data):
            request_data = load_request_data(definition.request_schema)
            page = self.page_cls.from_query_string(self.page_schema(), {})

            result = definition.func(**merge_data(
                path_data,
                merge_data(
                    request_data,
                    page.to_dict(func=identity),
                ),
            ))

            response_data, headers = page.to_paginated_list(result, ns, Operation.CreateCollection)
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                paginated_list_schema,
                response_data,
                headers=headers,
                response_format=response_format,
            )

        create_collection.__doc__ = "Create the collection of {}".format(pluralize(ns.subject_name))


def configure_crud(graph, ns, mappings):
    """
    Register CRUD endpoints for a resource object.

    :param mappings: a dictionary from operations to tuple, where each tuple contains
                     the target function and zero or more marshmallow schemas according
                     to the signature of the "register_<foo>_endpoint" functions

    Example mapping:

        {
            Operation.Create: (create_foo, NewFooSchema(), FooSchema()),
            Operation.Delete: (delete_foo,),
            Operation.Retrieve: (retrieve_foo, FooSchema()),
            Operation.Search: (search_foo, SearchFooSchema(), FooSchema(), [ResponseFormats.CSV]),
        }

    """
    convention = CRUDConvention(graph)
    convention.configure(ns, mappings)
