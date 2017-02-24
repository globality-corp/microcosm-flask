"""
Alias convention tests.

"""
from hamcrest import (
    assert_that,
    contains,
    equal_to,
    is_,
)
from json import loads
from six import b, BytesIO

from microcosm.api import create_object_graph

from microcosm_flask.namespaces import Namespace
from microcosm_flask.conventions.base import EndpointDefinition
from microcosm_flask.conventions.swagger import configure_swagger
from microcosm_flask.conventions.upload import configure_upload
from microcosm_flask.operations import Operation
from microcosm_flask.swagger.definitions import build_path


def upload_file(files, **kwargs):
    pass


UPLOAD_MAPPINGS = {
    Operation.Upload: EndpointDefinition(
        func=upload_file
    ),
}


class TestAlias(object):

    def setup(self):
        self.graph = create_object_graph(name="example", testing=True)

        self.ns = Namespace(subject="file")
        configure_upload(self.graph, self.ns, UPLOAD_MAPPINGS)
        configure_swagger(self.graph)

        self.client = self.graph.flask.test_client()

    def test_url_for(self):
        with self.graph.app.test_request_context():
            url = self.ns.url_for(Operation.Upload)
        assert_that(url, is_(equal_to("http://localhost/api/file")))

    def test_swagger_path(self):
        with self.graph.app.test_request_context():
            path = build_path(Operation.Upload, self.ns)
        assert_that(path, is_(equal_to("/api/file")))

    def test_swagger(self):
        response = self.client.get("/api/swagger")
        assert_that(response.status_code, is_(equal_to(200)))
        data = loads(response.data)

        assert_that(data["paths"]["/file"]["post"]["consumes"], contains("multipart/form-data"))

    def test_upload(self):
        response = self.client.post(
            "/api/file",
            data=dict(
                file=(BytesIO(b("Hello World\n")), "hello.txt"),
            ),
        )
        assert_that(response.status_code, is_(equal_to(204)))
