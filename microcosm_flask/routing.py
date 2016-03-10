"""
Routing registration support.

Intercepts Flask's normal route registration to inject conventions.

"""
from flask_cors import cross_origin

from microcosm.api import binding, defaults


@binding("route")
@defaults(
    enable_audit=True,
    enable_cors=True,
    path_prefix="/api",
)
def configure_route_decorator(graph):
    """
    Configure a flask route decorator that operations on `Operation` objects.

    By default, enables CORS support, assuming that service APIs are not exposed
    directly to browsers except when using API browsing tools.

    Usage:

        @graph.route("/foo", Operation.Search, "foo")
        def search_foo():
            pass

    """
    def route(path, operation, obj):
        def decorator(func):
            if graph.config.route.enable_cors:
                func = cross_origin(supports_credentials=True)(func)

            # keep audit decoration last (before registering the route) so that
            # errors raised by other decorators are captured in the audit trail
            if graph.config.route.enable_audit:
                func = graph.audit(func)

            graph.flask.route(
                graph.config.route.path_prefix + path,
                # for blueprints, the endpoint is operation.value.name
                # because Flask automatically prefixes blueprint endpoints with "obj."
                endpoint=operation.name_for(obj),
                methods=[operation.value.method],
            )(func)
            return func
        return decorator
    return route
