"""
Conventions for canonical relation endpoints (mapping one resource to another).

For relations, endpoint definitions require that the `Namespace` contain *both*
a subject and an object.

"""
from functools import wraps

from inflection import pluralize
from marshmallow import Schema

from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.encoding import (
    dump_response_data,
    encode_id_header,
    load_query_string_data,
    load_request_data,
    merge_data,
    require_response_data,
)
from microcosm_flask.conventions.registry import qs, request, response
from microcosm_flask.operations import Operation
from microcosm_flask.paging import OffsetLimitPage, identity


class RelationConvention(Convention):

    @property
    def page_cls(self):
        return OffsetLimitPage

    def __init__(self, graph):
        super(RelationConvention, self).__init__(graph)

    def configure_createfor(self, ns, definition):
        """
        Register a create-for relation endpoint.

        The definition's func should be a create function, which must:
        - accept kwargs for the new instance creation parameters
        - return the created instance

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        @self.add_route(ns.relation_path, Operation.CreateFor, ns)
        @request(definition.request_schema)
        @response(definition.response_schema)
        @wraps(definition.func)
        def create(**path_data):
            request_data = load_request_data(definition.request_schema)
            response_data = require_response_data(definition.func(**merge_data(path_data, request_data)))
            headers = encode_id_header(response_data)
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                definition.response_schema,
                response_data,
                Operation.CreateFor.value.default_code,
                headers=headers,
                response_format=response_format,
            )

        create.__doc__ = "Create a new {} relative to a {}".format(pluralize(ns.object_name), ns.subject_name)

    def configure_deletefor(self, ns, definition):
        """
        Register a delete-for relation endpoint.

        The definition's func should be a delete function, which must:
        - accept kwargs for path data
        - return truthy/falsey

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        @self.add_route(ns.relation_path, Operation.DeleteFor, ns)
        @wraps(definition.func)
        def delete(**path_data):
            headers = dict()
            response_data = dict()
            require_response_data(definition.func(**path_data))
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                "",
                None,
                status_code=Operation.DeleteFor.value.default_code,
                headers=headers,
                response_format=response_format,
            )

        delete.__doc__ = "Delete a {} relative to a {}".format(pluralize(ns.object_name), ns.subject_name)

    def configure_replacefor(self, ns, definition):
        """
        Register a replace-for relation endpoint.

        For typical usage, this relation is not strictly required; once an object exists and has its own ID,
        it is better to operate on it directly via dedicated CRUD routes.
        However, in some cases, the composite key of (subject_id, object_id) is required to look up the object.
        This happens, for example, when using DynamoDB where an object which maintains both a hash key and a range key
        requires specifying them both for access.

        The definition's func should be a replace function, which must:

        - accept kwargs for the new instance replacement parameters
        - return the instance

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        @self.add_route(ns.relation_path, Operation.ReplaceFor, ns)
        @request(definition.request_schema)
        @response(definition.response_schema)
        @wraps(definition.func)
        def replace(**path_data):
            headers = dict()
            request_data = load_request_data(definition.request_schema)
            response_data = require_response_data(definition.func(**merge_data(path_data, request_data)))
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                definition.response_schema,
                response_data,
                status_code=Operation.ReplaceFor.value.default_code,
                headers=headers,
                response_format=response_format,
            )

        replace.__doc__ = "Replace a {} relative to a {}".format(pluralize(ns.object_name), ns.subject_name)

    def configure_updatefor(self, ns, definition):
        """
        Register an update-for relation endpoint.

        For typical usage, this relation is not strictly required; once an object exists and has its own ID,
        it is better to operate on it directly via dedicated CRUD routes.
        However, in some cases, the composite key of (subject_id, object_id) is required to look up the object.
        This happens, for example, when using DynamoDB where an object which maintains both a hash key and a range key
        requires specifying them both for access.

        The definition's func should be an update function, which must:

        - accept kwargs for the new instance replacement parameters
        - return the instance

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        @self.add_route(ns.relation_path, Operation.UpdateFor, ns)
        @request(definition.request_schema)
        @response(definition.response_schema)
        @wraps(definition.func)
        def replace(**path_data):
            headers = dict()
            request_data = load_request_data(definition.request_schema)
            response_data = require_response_data(definition.func(**merge_data(path_data, request_data)))
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                definition.response_schema,
                response_data,
                status_code=Operation.UpdateFor.value.default_code,
                headers=headers,
                response_format=response_format,
            )

        replace.__doc__ = "Replace a {} relative to a {}".format(pluralize(ns.object_name), ns.subject_name)

    def configure_retrievefor(self, ns, definition):
        """
        Register a relation endpoint.

        The definition's func should be a retrieve function, which must:
        - accept kwargs for path data and optional request data
        - return an item

        The definition's request_schema will be used to process query string arguments, if any.

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        request_schema = definition.request_schema or Schema()

        @self.add_route(ns.relation_path, Operation.RetrieveFor, ns)
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

        retrieve.__doc__ = "Retrieve {} relative to a {}".format(pluralize(ns.object_name), ns.subject_name)

    def configure_searchfor(self, ns, definition):
        """
        Register a relation endpoint.

        The definition's func should be a search function, which must:
        - accept kwargs for the query string (minimally for pagination)
        - return a tuple of (items, count, context) where count is the total number of items
          available (in the case of pagination) and context is a dictionary providing any
          needed context variables for constructing pagination links

        The definition's request_schema will be used to process query string arguments.

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        paginated_list_schema = self.page_cls.make_paginated_list_schema_class(
            ns.object_ns,
            definition.response_schema,
        )()

        @self.add_route(ns.relation_path, Operation.SearchFor, ns)
        @qs(definition.request_schema)
        @response(paginated_list_schema)
        @wraps(definition.func)
        def search(**path_data):
            page = self.page_cls.from_query_string(definition.request_schema)
            result = definition.func(**merge_data(path_data, page.to_dict(func=identity)))
            response_data, headers = page.to_paginated_list(result, ns, Operation.SearchFor)
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                paginated_list_schema,
                response_data,
                headers=headers,
                response_format=response_format,
            )

        search.__doc__ = "Search for {} relative to a {}".format(pluralize(ns.object_name), ns.subject_name)


def configure_relation(graph, ns, mappings):
    """
    Register relation endpoint(s) between two resources.

    """
    convention = RelationConvention(graph)
    convention.configure(ns, mappings)
