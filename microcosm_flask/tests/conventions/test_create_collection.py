from hamcrest import (
    all_of,
    assert_that,
    equal_to,
    has_entry,
    has_items,
    has_key,
    is_,
    is_not,
)
from json import dumps, loads
from marshmallow import fields, Schema
from microcosm.api import create_object_graph

from microcosm_flask.conventions.base import EndpointDefinition
from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.conventions.swagger import configure_swagger
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation
from microcosm_flask.swagger.definitions import build_path


def create_collection(text, offset, limit):
    return dict(text=text), 1


class FooRequestSchema(Schema):
    text = fields.String(required=True)


class FooResponseSchema(Schema):
    text = fields.String(request=True)


FOO_MAPPINGS = {
    Operation.CreateCollection: EndpointDefinition(
        func=create_collection,
        request_schema=FooRequestSchema(),
        response_schema=FooResponseSchema(),
    ),
}


class TestCreateCollection(object):

    def setup(self):
        self.graph = create_object_graph(name="example", testing=True)

        self.ns = Namespace(subject="foo")

        configure_crud(self.graph, self.ns, FOO_MAPPINGS)
        configure_swagger(self.graph)

        self.client = self.graph.flask.test_client()

    def test_create_collection_url(self):
        with self.graph.app.test_request_context():
            url = self.ns.url_for(Operation.CreateCollection)

        assert_that(url, is_(equal_to("http://localhost/api/foo")))

    def test_swagger_path(self):
        with self.graph.app.test_request_context():
            path = build_path(Operation.CreateCollection, self.ns)

        assert_that(path, is_(equal_to("/api/foo")))

    def test_swagger(self):
        response = self.client.get("/api/swagger")
        assert_that(response.status_code, is_(equal_to(200)))
        data = loads(response.data)["paths"]["/foo"]["post"]

        assert_that(
            data["parameters"],
            has_items(
                has_entry(
                    "in",
                    "body",
                ),
                has_entry(
                    "schema",
                    has_entry(
                        "$ref",
                        "#/definitions/FooRequest",
                    ),
                ),
            ),
        )
        assert_that(
            data["responses"],
            all_of(
                has_key("200"),
                is_not(has_key("204")),
                has_entry(
                    "200",
                    has_entry(
                        "schema",
                        has_entry(
                            "$ref",
                            "#/definitions/FooList",
                        ),
                    ),
                ),
            ),
        )

    def test_create_collection(self):
        text = "Some text..."
        response = self.client.post(
            "/api/foo",
            data=dumps({"text": text}),
        )

        assert_that(response.status_code, is_(equal_to(200)))
        assert_that(loads(response.data), is_(equal_to({
            "count": 1,
            "offset": 0,
            "limit": 20,
            "items": [{"text": text}],
            "_links": {
                "self": {
                    "href": "http://localhost/api/foo?offset=0&limit=20",
                },
            },
        })))
