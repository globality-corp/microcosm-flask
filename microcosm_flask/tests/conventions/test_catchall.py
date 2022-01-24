"""
Test catch-all route

"""
from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph


def make_routes(graph):
    """
    Create a few routes

    """
    @graph.flask.route("/")
    def root_route():
        return "root"

    @graph.flask.route("/something/<string:id>")
    def id_route(id):
        if id in ["123", "456"]:
            return id
        return "Resource not found", 404


class TestCatchall:
    def setup(self):
        self.graph = create_object_graph(name="example", testing=True)
        self.graph.use("catchall_convention")

        make_routes(self.graph)

        self.client = self.graph.flask.test_client()

    def test_catchall(self):
        # Check that the catch-all route works
        response_get = self.client.get("/api/v1/nonexistent_uri")
        assert_that(response_get.status_code, is_(equal_to(421)))

        response_post = self.client.get("/api/v1/nonexistent_uri")
        assert_that(response_post.status_code, is_(equal_to(421)))

        # Note that the catchall convention overrides the usual HTTP 405 cases
        response_id = self.client.post("/something/123")
        assert_that(response_id.status_code, is_(equal_to(421)))

        # Check that existing routes still resolve correctly
        response_root = self.client.get("/")
        assert_that(response_root.status_code, is_(equal_to(200)))

        response_id = self.client.get("/something/123")
        assert_that(response_id.status_code, is_(equal_to(200)))

        response_id = self.client.get("/something/789")
        assert_that(response_id.status_code, is_(equal_to(404)))
