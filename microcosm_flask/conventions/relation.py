"""
Conventions for canonical relation endpoints (mapping one resource to another).

For relations, endpoint definitions require that the `Namespace` contain *both*
a subject and an object.

"""
from flask import jsonify
from inflection import pluralize
from marshmallow import Schema

from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.encoding import (
    dump_response_data,
    load_query_string_data,
    load_request_data,
    merge_data,
    require_response_data,
)
from microcosm_flask.conventions.registry import qs, request, response
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation
from microcosm_flask.paging import Page, PaginatedList, make_paginated_list_schema


class RelationConvention(Convention):

    def __init__(self, graph, paginated_list_class=PaginatedList):
        super(RelationConvention, self).__init__(graph)

        self.paginated_list_class = paginated_list_class

    def configure_createfor(self, ns, definition):
        """
        Register a create-for relation endpoint.

        The definition's func should be a create function, which must:
        - accept kwargs for the new instance creation parameters
        - return the created instance

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        @self.graph.route(ns.relation_path, Operation.CreateFor, ns)
        @request(definition.request_schema)
        @response(definition.response_schema)
        def create(**path_data):
            request_data = load_request_data(definition.request_schema)
            response_data = require_response_data(definition.func(**merge_data(path_data, request_data)))
            return dump_response_data(definition.response_schema, response_data, Operation.CreateFor.value.default_code)

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
        @self.graph.route(ns.instance_path, Operation.DeleteFor, ns)
        def delete(**path_data):
            require_response_data(definition.func(**path_data))
            return "", Operation.DeleteFor.value.default_code

        delete.__doc__ = "Delete a {} relative to a {}".format(pluralize(ns.object_name), ns.subject_name)

    def configure_replacefor(self, ns, definition):
        """
        Register a replace-for relation endpoint.

        The definition's func should be a replace function, which must:
        - accept kwargs for the new-or-updated instance parameters
        - return the created or updated instance

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        @self.graph.route(ns.relation_path, Operation.ReplaceFor, ns)
        @request(definition.request_schema)
        @response(definition.response_schema)
        def replace(**path_data):
            request_data = load_request_data(definition.request_schema)
            response_data = require_response_data(definition.func(**merge_data(path_data, request_data)))
            return dump_response_data(
                definition.response_schema,
                response_data,
                Operation.ReplaceFor.value.default_code,
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

        @self.graph.route(ns.relation_path, Operation.RetrieveFor, ns)
        @qs(request_schema)
        @response(definition.response_schema)
        def retrieve(**path_data):
            request_data = load_query_string_data(request_schema)
            response_data = require_response_data(definition.func(**merge_data(path_data, request_data)))
            return dump_response_data(definition.response_schema, response_data)

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
        paginated_list_schema = make_paginated_list_schema(ns.object_ns, definition.response_schema)()

        @self.graph.route(ns.relation_path, Operation.SearchFor, ns)
        @qs(definition.request_schema)
        @response(paginated_list_schema)
        def search(**path_data):
            request_data = load_query_string_data(definition.request_schema)
            page = Page.from_query_string(request_data)
            items, count, context = definition.func(**merge_data(path_data, request_data))
            # TODO: use the schema for encoding
            return jsonify(
                self.paginated_list_class(
                    ns,
                    page,
                    items,
                    count,
                    definition.response_schema,
                    Operation.SearchFor,
                    **context
                ).to_dict()
            )

        search.__doc__ = "Search for {} relative to a {}".format(pluralize(ns.object_name), ns.subject_name)


def configure_relation(graph, ns, mappings, path_prefix=""):
    """
    Register relation endpoint(s) between two resources.

    """
    ns = Namespace.make(ns, path=path_prefix)
    convention = RelationConvention(graph)
    convention.configure(ns, mappings)
