from hamcrest import assert_that, equal_to, is_, none
from microcosm.api import create_object_graph

from microcosm_flask.conventions.encoding import find_response_format
from microcosm_flask.enums import ResponseFormats


class TestEncoding(object):
    def setup(self):
        self.graph = create_object_graph(name="example", testing=True)

    def test_find_response_format(self):
        with self.graph.app.test_request_context(
            headers=dict(Accept=["application/pdf"])
        ):
            # PDF is not allowed by endpoint, return None (which may raise 406 - Not Acceptable)
            assert_that(
                find_response_format([ResponseFormats.JSON]),
                is_(none()),
            )

        with self.graph.app.test_request_context(
            headers=dict()
        ):
            # If no "Accept" header default to endpoint allowed formats
            assert_that(
                find_response_format([ResponseFormats.CSV]),
                equal_to(ResponseFormats.CSV),
            )
            # If that isn't specified default to JSON
            assert_that(
                find_response_format([]),
                equal_to(ResponseFormats.JSON),
            )

        with self.graph.app.test_request_context(
            headers=dict(Accept=["text/csv"])
        ):
            # If Accept header is present and that format is allowed, return it
            assert_that(
                find_response_format([ResponseFormats.CSV, ResponseFormats.JSON]),
                equal_to(ResponseFormats.CSV),
            )
