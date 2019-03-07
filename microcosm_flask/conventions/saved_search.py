"""
Saved search convention.

"""
from functools import wraps

from inflection import pluralize

from microcosm_flask.conventions.base import Convention
from microcosm_flask.conventions.encoding import dump_response_data, load_request_data, merge_data
from microcosm_flask.conventions.registry import request, response
from microcosm_flask.operations import Operation
from microcosm_flask.paging import OffsetLimitPage, identity


class SavedSearchConvention(Convention):

    @property
    def page_cls(self):
        return OffsetLimitPage

    def configure_savedsearch(self, ns, definition):
        """
        Register a saved search endpoint.

        The definition's func should be a search function, which must:
        - accept kwargs for the request data
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

        @self.add_route(ns.collection_path, Operation.SavedSearch, ns)
        @request(definition.request_schema)
        @response(paginated_list_schema)
        @wraps(definition.func)
        def saved_search(**path_data):
            request_data = load_request_data(definition.request_schema)
            page = self.page_cls.from_dict(request_data)
            request_data.update(page.to_dict(func=identity))
            result = definition.func(**merge_data(path_data, request_data))
            response_data, headers = page.to_paginated_list(result, ns, Operation.SavedSearch)
            definition.header_func(headers, response_data)
            response_format = self.negotiate_response_content(definition.response_formats)
            return dump_response_data(
                paginated_list_schema,
                response_data,
                headers=headers,
                response_format=response_format,
            )

        saved_search.__doc__ = "Persist and return the search results of {}".format(pluralize(ns.subject_name))


def configure_saved_search(graph, ns, mappings):
    convention = SavedSearchConvention(graph)
    convention.configure(ns, mappings)
