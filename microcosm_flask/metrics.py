"""
Metrics extensions for routes.

"""
from microcosm.api import defaults, typed
from microcosm.config.types import boolean
from microcosm.errors import NotBoundError


@defaults(
    enabled=typed(boolean, default_value=True),
)
class RouteMetrics:

    def __init__(self, graph):
        self.metrics = self.get_metrics(graph)
        self.enabled = bool(
            self.metrics
            and self.metrics.host != "localhost"
            and graph.config.route_metrics.enabled
        )
        self.graph = graph

    def get_metrics(self, graph):
        """
        Fetch the metrics client from the graph.

        Metrics will be disabled if the not configured.

        """
        try:
            return graph.metrics
        except NotBoundError:
            return None

    def __call__(self, endpoint):
        from microcosm_flask.metrics_classifier import StatusCodeClassifier

        def decorator(func):
            key = "route"
            tags = [
                f"endpoint:{endpoint}",
                "backend_type:microcosm_flask",
            ]
            counting = self.graph.metrics_counting(
                key,
                tags=tags,
                classifier_cls=StatusCodeClassifier,
            )
            timing = self.graph.metrics_timing(
                key,
                tags=tags,
            )
            return timing(counting(func))

        return decorator
