"""
Metrics tests.

"""
from unittest import SkipTest
from unittest.mock import ANY

from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph, load_from_dict
from werkzeug.exceptions import NotFound

from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


class TestRouteMetrics:

    def setup(self):
        try:
            import microcosm_metrics  # noqa: F401
        except ImportError:
            raise SkipTest

        self.loader = load_from_dict(
            metrics=dict(
                host="statsd",
            ),
        )
        self.graph = create_object_graph("example", testing=True, loader=self.loader)
        self.graph.use(
            "metrics",
            "flask",
            "route",
        )
        self.client = self.graph.flask.test_client()

        self.ns = Namespace(
            subject="foo",
            version="v1",
        )

    def test_success_metrics(self):
        """
        A standard 200 response has both timing and counting metrics.
        Classifier tag comes from StatusCodeClassifier

        """
        @self.graph.route(self.ns.collection_path, Operation.Search, self.ns)
        def foo():
            return ""

        response = self.client.get("api/v1/foo")
        assert_that(response.status_code, is_(equal_to(200)))

        self.graph.metrics.histogram.assert_called_with(
            "route",
            ANY,
            tags=[
                "endpoint:foo.search.v1",
                "backend_type:microcosm_flask",
            ],
        )
        self.graph.metrics.increment.assert_called_with(
            "route.call.count",
            tags=[
                "endpoint:foo.search.v1",
                "backend_type:microcosm_flask",
                "classifier:200",
            ],
        )

    def test_different_status_code_metrics(self):
        """
        A different status code response has both timing and counting metrics.
        Classifier tag comes from StatusCodeClassifier

        """
        @self.graph.route(self.ns.collection_path, Operation.Search, self.ns)
        def foo():
            return "", 204

        response = self.client.get("api/v1/foo")
        assert_that(response.status_code, is_(equal_to(204)))

        self.graph.metrics.histogram.assert_called_with(
            "route",
            ANY,
            tags=[
                "endpoint:foo.search.v1",
                "backend_type:microcosm_flask",
            ],
        )
        self.graph.metrics.increment.assert_called_with(
            "route.call.count",
            tags=[
                "endpoint:foo.search.v1",
                "backend_type:microcosm_flask",
                "classifier:204",
            ],
        )

    def test_exception_metrics(self):
        """
        An exception response has both timing and counting metrics.
        Classifier tag comes from StatusCodeClassifier

        """
        @self.graph.route(self.ns.collection_path, Operation.Search, self.ns)
        def foo():
            raise NotFound

        response = self.client.get("api/v1/foo")
        assert_that(response.status_code, is_(equal_to(404)))

        self.graph.metrics.histogram.assert_called_with(
            "route",
            ANY,
            tags=[
                "endpoint:foo.search.v1",
                "backend_type:microcosm_flask",
            ]
        )
        self.graph.metrics.increment.assert_called_with(
            "route.call.count",
            tags=[
                "endpoint:foo.search.v1",
                "backend_type:microcosm_flask",
                "classifier:404",
            ],
        )
