"""
Metrics tests.

"""
from unittest import SkipTest
from unittest.mock import ANY

from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph
from werkzeug.exceptions import NotFound

from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


class TestRouteMetrics:

    def setup(self):
        try:
            import microcosm_metrics  # noqa
        except ImportError:
            raise SkipTest

        self.graph = create_object_graph("example", testing=True)
        self.graph.use(
            "datadog_statsd",
            "flask",
            "route",
        )
        self.client = self.graph.flask.test_client()

        self.ns = Namespace(
            enable_metrics=True,
            subject="foo",
            version="v1",
        )

    def test_success_metrics(self):
        """
        A standard 200 response has both timing and counting metrics.

        """
        @self.graph.route(self.ns.collection_path, Operation.Search, self.ns)
        def foo():
            return ""

        response = self.client.get("api/v1/foo")
        assert_that(response.status_code, is_(equal_to(200)))

        self.graph.metrics.histogram.assert_called_with(
            "undefined.example.foo.search.v1",
            ANY,
        )
        self.graph.metrics.increment.assert_called_with(
            "undefined.example.foo.search.v1.200.count",
        )

    def test_different_status_code_metrics(self):
        """
        A different status code response has both timing and counting metrics.

        """
        @self.graph.route(self.ns.collection_path, Operation.Search, self.ns)
        def foo():
            return "", 204

        response = self.client.get("api/v1/foo")
        assert_that(response.status_code, is_(equal_to(204)))

        self.graph.metrics.histogram.assert_called_with(
            "undefined.example.foo.search.v1",
            ANY,
        )
        self.graph.metrics.increment.assert_called_with(
            "undefined.example.foo.search.v1.204.count",
        )

    def test_exception_metrics(self):
        """
        An exception response has both timing and counting metrics.

        """
        @self.graph.route(self.ns.collection_path, Operation.Search, self.ns)
        def foo():
            raise NotFound

        response = self.client.get("api/v1/foo")
        assert_that(response.status_code, is_(equal_to(404)))

        self.graph.metrics.histogram.assert_called_with(
            "undefined.example.foo.search.v1",
            ANY,
        )
        self.graph.metrics.increment.assert_called_with(
            "undefined.example.foo.search.v1.404.count",
        )
