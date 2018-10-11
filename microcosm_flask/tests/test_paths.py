"""
Test path building.

"""
from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph


class TestRoutePathBuilder:

    def setup(self):
        self.graph = create_object_graph("microcosm-path", testing=True)
        self.build_route_path = self.graph.build_route_path
        self.graph.lock()

    def test_simple_path(self):
        assert_that(
            self.build_route_path("foo"),
            is_(equal_to("/api/foo")),
        )

    def test_simple_path_with_leading_slash(self):
        assert_that(
            self.build_route_path("/foo"),
            is_(equal_to("/api/foo")),
        )

    def test_simple_path_with_trailing_slash(self):
        assert_that(
            self.build_route_path("foo/"),
            is_(equal_to("/api/foo")),
        )

    def test_slash(self):
        assert_that(
            self.build_route_path("/"),
            is_(equal_to("/api")),
        )

    def test_empty(self):
        assert_that(
            self.build_route_path(""),
            is_(equal_to("/api")),
        )

    def test_override_prefix(self):
        assert_that(
            self.build_route_path("/ping", "/foo"),
            is_(equal_to("/foo/ping")),
        )

    def test_override_slash_prefix(self):
        assert_that(
            self.build_route_path("ping", "/"),
            is_(equal_to("/ping")),
        )

    def test_override_empty_prefix(self):
        assert_that(
            self.build_route_path("/ping", ""),
            is_(equal_to("/ping")),
        )
