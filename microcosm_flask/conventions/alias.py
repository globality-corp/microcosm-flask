"""
Conventions for aliasing endpoints.

"""
from functools import wraps

from flask import redirect
from microcosm_flask.conventions.base import Convention
from microcosm_flask.naming import name_for
from microcosm_flask.operations import Operation


class AliasConvention(Convention):

    def configure_alias(self, ns, definition):
        """
        Register an alias endpoint which will redirect to a resource's retrieve endpoint.

        Note that the retrieve endpoint MUST be registered prior to the alias endpoint.

        The definition's func should be a retrieve function, which must:
        - accept kwargs for path data
        - return a resource

        :param ns: the namespace
        :param definition: the endpoint definition

        """
        @self.add_route(ns.alias_path, Operation.Alias, ns)
        @wraps(definition.func)
        def retrieve(**path_data):
            resource = definition.func(**path_data)

            kwargs = dict()
            identifier = "{}_id".format(name_for(ns.subject))
            kwargs[identifier] = resource.id
            url = ns.url_for(Operation.Retrieve, **kwargs)

            return redirect(url)

        retrieve.__doc__ = "Alias a {} by name".format(ns.subject_name)


def configure_alias(graph, ns, mappings):
    """
    Register Alias endpoints for a resource object.

    """
    convention = AliasConvention(graph)
    convention.configure(ns, mappings)
