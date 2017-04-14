"""
Routing registration support.

Intercepts Flask's normal route registration to inject conventions.

"""
from distutils.util import strtobool

from flask_cors import cross_origin
from microcosm.api import defaults
from microcosm_logging.decorators import context_logger


def make_path(graph, path):
    return graph.config.route.path_prefix + path


@defaults(
    converters=[
        "uuid",
    ],
    enable_audit="true",
    enable_basic_auth="false",
    enable_context_logger="true",
    enable_cors="true",
    enable_metrics="false",
    path_prefix="/api",
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
    enable_audit = strtobool(graph.config.route.enable_audit)
    enable_basic_auth = strtobool(graph.config.route.enable_basic_auth)
    enable_context_logger = strtobool(graph.config.route.enable_context_logger)
    enable_cors = strtobool(graph.config.route.enable_cors)
    enable_metrics = strtobool(graph.config.route.enable_metrics)

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
            endpoint_path = make_path(graph, path)

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

            if enable_metrics or ns.enable_metrics:
                from microcosm_flask.metrics import StatusCodeClassifier
                func = graph.metrics_counting(endpoint, classifier_cls=StatusCodeClassifier)(func)
                func = graph.metrics_timing(endpoint)(func)

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
