"""
Routing registration support.

Intercepts Flask's normal route registration to inject conventions.

"""
from flask_cors import cross_origin
from microcosm.api import defaults, typed
from microcosm.config.types import boolean
from microcosm_logging.decorators import context_logger


@defaults(
    converters=[
        "uuid",
    ],
    enable_audit=typed(boolean, default_value=True),
    enable_basic_auth=typed(boolean, default_value=False),
    enable_context_logger=typed(boolean, default_value=True),
    enable_cors=typed(boolean, default_value=True),
)
def configure_route_decorator(graph):
    """
    Configure a flask route decorator that operates on `Operation` and `Namespace` objects.

    By default, enables CORS support, assuming that service APIs are not exposed
    directly to browsers except when using API browsing tools.

    Usage:

        @graph.route(ns.collection_path, Operation.Search, ns)
        def search_foo():
            pass

    """
    enable_audit = graph.config.route.enable_audit
    enable_basic_auth = graph.config.route.enable_basic_auth
    enable_context_logger = graph.config.route.enable_context_logger
    enable_cors = graph.config.route.enable_cors

    # routes depends on converters
    graph.use(*graph.config.route.converters)

    def route(path, operation, ns):
        """
        :param path: a URI path, possibly derived from a property of the `ns`
        :param operation: an `Operation` enum value
        :param ns: a `Namespace` instance

        """
        def decorator(func):
            endpoint = ns.endpoint_for(operation)
            endpoint_path = graph.build_route_path(path, ns.prefix)

            if enable_cors:
                func = cross_origin(supports_credentials=True)(func)

            if enable_basic_auth or ns.enable_basic_auth:
                func = graph.basic_auth.required(func)

            if enable_context_logger and ns.controller is not None:
                func = context_logger(
                    graph.request_context,
                    func,
                    parent=ns.controller,
                )

            # set the opaque component data_func to look at the flask request context
            func = graph.opaque.initialize(graph.request_context)(func)

            if graph.route_metrics.enabled:
                func = graph.route_metrics(endpoint)(func)

            if graph.memory_profiler.enabled:
                func = graph.memory_profiler.snapshot_at_intervals(func)

            # keep audit decoration last (before registering the route) so that
            # errors raised by other decorators are captured in the audit trail
            if enable_audit:
                func = graph.audit(func)

            graph.app.route(
                endpoint_path,
                endpoint=endpoint,
                methods=[operation.value.method],
            )(func)
            return func
        return decorator
    return route
