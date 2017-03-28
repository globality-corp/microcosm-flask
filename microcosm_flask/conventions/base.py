"""
Convention base class.

"""
from microcosm_flask.operations import Operation


class RouteAlreadyRegisteredException(Exception):
    pass


class EndpointDefinition(tuple):
    """
    A definition for an endpoint.

    """
    def __new__(cls, func=None, request_schema=None, response_schema=None):
        """
        :param func: a function to process request data and return response data
        :param request_schema: a marshmallow schema to decode/validate request data
        :param response_schema: a marshmallow schema to encode response data
        """
        return tuple.__new__(EndpointDefinition, (func, request_schema, response_schema))

    @property
    def func(self):
        return self[0]

    @property
    def request_schema(self):
        return self[1]

    @property
    def response_schema(self):
        return self[2]


class Convention(object):
    """
    A convention is a recipe for applying Flask-compatible functions to a namespace.

    """
    def __init__(self, graph):
        self.graph = graph
        self._registered_routes = set()

    def configure(self, ns, mappings=None, **kwargs):
        """
        Apply mappings to a namespace.

        """
        if mappings is None:
            mappings = dict()
        mappings.update(kwargs)

        for operation, definition in mappings.items():
            try:
                configure_func = self._find_func(operation)
            except AttributeError:
                pass
            else:
                configure_func(ns, self._make_definition(definition))

    def add_route(self, path, operation, ns):
        route = (operation.value.method, path)

        if route in self._registered_routes:
            raise RouteAlreadyRegisteredException(route)

        self._registered_routes.add(route)

        return self.graph.route(path, operation, ns)

    def _find_func(self, operation):
        """
        Find the function to use to configure the given operation.

        The input might be an `Operation` enum or a string.

        """
        if isinstance(operation, Operation):
            operation_name = operation.name.lower()
        else:
            operation_name = operation.lower()

        return getattr(self, "configure_{}".format(operation_name))

    def _make_definition(self, definition):
        """
        Generate a definition.

        The input might already be a `EndpointDefinition` or it might be a tuple.

        """
        if not definition:
            return EndpointDefinition()
        if isinstance(definition, EndpointDefinition):
            return definition
        elif len(definition) == 1:
            return EndpointDefinition(
                func=definition[0],
            )
        elif len(definition) == 2:
            return EndpointDefinition(
                func=definition[0],
                response_schema=definition[1],
            )
        elif len(definition) == 3:
            return EndpointDefinition(
                func=definition[0],
                request_schema=definition[1],
                response_schema=definition[2],
            )
