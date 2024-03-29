"""
Query operation tests.

"""
from json import loads

from hamcrest import assert_that, equal_to, is_
from marshmallow import Schema, fields
from microcosm.api import create_object_graph

from microcosm_flask.conventions.encoding import dump_response_data, load_query_string_data
from microcosm_flask.conventions.registry import qs, response
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


class QueryStringSchema(Schema):
    required_value = fields.String(required=True)
    optional_value = fields.String(required=False)


class QueryResultSchema(Schema):
    result = fields.Boolean(required=True)
    value = fields.String(required=True)


def make_query(graph, ns, request_schema, response_schema):
    """
    Create an example query route.

    """

    @graph.route("/v1/foo/get", Operation.Query, ns)
    @qs(request_schema)
    @response(response_schema)
    def foo_query():
        """
        My doc string
        """
        request_data = load_query_string_data(request_schema)
        response_data = dict(
            result=True,
            value=request_data["required_value"],
        )
        return dump_response_data(
            response_schema, response_data, Operation.Query.value.default_code
        )


class TestQuery:
    def setup_method(self):
        # override configuration to use "query" operations for swagger
        def loader(metadata):
            return dict(
                swagger_convention=dict(
                    # default behavior appends this list to defaults; use a tuple to override
                    operations=["query"],
                    version="v1",
                ),
            )

        self.graph = create_object_graph(name="example", testing=True, loader=loader)
        self.graph.use("swagger_convention")
        self.ns = Namespace(subject="foo")

        make_query(self.graph, self.ns, QueryStringSchema(), QueryResultSchema())

        self.client = self.graph.flask.test_client()

    def test_url_for(self):
        """
        The operation knowns how to resolve a URI for this query.

        """
        with self.graph.flask.test_request_context():
            assert_that(
                self.ns.url_for(Operation.Query),
                is_(equal_to("http://localhost/api/v1/foo/get")),
            )

    def test_query(self):
        """
        The query can take advantage of boilerplate encoding/decoding.

        """
        uri = "/api/v1/foo/get"
        query_string = {
            "required_value": "bar",
        }
        response = self.client.get(uri, query_string=query_string)
        assert_that(response.status_code, is_(equal_to(200)))
        assert_that(
            loads(response.get_data().decode("utf-8")),
            is_(
                equal_to(
                    {
                        "result": True,
                        "value": "bar",
                    }
                )
            ),
        )

    def test_swagger(self):
        """
        Swagger definitions including this operation.

        """
        response = self.client.get(
            "/api/v1/swagger", query_string=dict(validate_schema=True)
        )
        assert_that(response.status_code, is_(equal_to(200)))
        swagger = loads(response.get_data().decode("utf-8"))
        # we have the swagger docs endpoint too, which is implemented as a query.
        # ignore it here for now.
        del swagger["paths"]["/swagger/docs"]
        assert_that(
            swagger["paths"],
            is_(
                equal_to(
                    {
                        "/foo/get": {
                            "get": {
                                "description": "My doc string",
                                "tags": ["foo"],
                                "responses": {
                                    "default": {
                                        "description": "An error occurred",
                                        "schema": {
                                            "$ref": "#/definitions/Error",
                                        },
                                    },
                                    "200": {
                                        "description": "My doc string",
                                        "schema": {
                                            "$ref": "#/definitions/QueryResult",
                                        },
                                    },
                                },
                                "parameters": [
                                    {
                                        "in": "header",
                                        "name": "X-Response-Skip-Null",
                                        "required": False,
                                        "type": "string",
                                        "description": "Remove fields with null values from the response.",
                                    },
                                    {
                                        "required": False,
                                        "type": "string",
                                        "name": "optional_value",
                                        "in": "query",
                                    },
                                    {
                                        "required": True,
                                        "type": "string",
                                        "name": "required_value",
                                        "in": "query",
                                    },
                                ],
                                "operationId": "query",
                            }
                        }
                    }
                )
            ),
        )
