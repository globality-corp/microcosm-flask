"""
Command operation tests.

"""
from json import dumps, loads

from hamcrest import assert_that, equal_to, is_
from marshmallow import Schema, fields
from microcosm.api import create_object_graph

from microcosm_flask.conventions.encoding import dump_response_data, load_request_data
from microcosm_flask.conventions.registry import request, response
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


class CommandArgumentSchema(Schema):
    value = fields.String(required=True)


class CommandResultSchema(Schema):
    result = fields.Boolean(required=True)
    value = fields.String(required=True)


def make_command(graph, ns, request_schema, response_schema):
    """
    Create an example command route.

    """
    @graph.route("/v1/foo/do", Operation.Command, ns)
    @request(request_schema)
    @response(response_schema)
    def foo_command():
        """
        My doc string
        """
        request_data = load_request_data(request_schema)
        response_data = dict(
            result=True,
            value=request_data["value"],
        )
        return dump_response_data(response_schema, response_data, Operation.Command.value.default_code)


class TestCommand:

    def setup(self):
        # override configuration to use "query" operations for swagger
        def loader(metadata):
            return dict(
                swagger_convention=dict(
                    # default behavior appends this list to defaults; use a tuple to override
                    operations=["command"],
                    version="v1",
                ),
            )

        self.graph = create_object_graph(name="example", testing=True, loader=loader)
        self.graph.use("swagger_convention")
        self.ns = Namespace(subject="foo")

        make_command(self.graph, self.ns, CommandArgumentSchema(), CommandResultSchema())

        self.client = self.graph.flask.test_client()

    def test_url_for(self):
        """
        The operation knowns how to resolve a URI for this command.

        """
        with self.graph.flask.test_request_context():
            assert_that(self.ns.url_for(Operation.Command), is_(equal_to("http://localhost/api/v1/foo/do")))

    def test_command(self):
        """
        The command can take advantage of boilerplate encoding/decoding.

        """
        uri = "/api/v1/foo/do"
        request_data = {
            "value": "bar",
        }
        response = self.client.post(uri, data=dumps(request_data))
        assert_that(response.status_code, is_(equal_to(200)))
        assert_that(loads(response.get_data().decode("utf-8")), is_(equal_to({
            "result": True,
            "value": "bar",
        })))

    def test_swagger(self):
        """
        Swagger definitions including this operation.

        """
        response = self.client.get("/api/v1/swagger")
        assert_that(response.status_code, is_(equal_to(200)))
        swagger = loads(response.get_data().decode("utf-8"))
        assert_that(swagger["paths"], is_(equal_to({
            "/foo/do": {
                "post": {
                    "tags": ["foo"],
                    "responses": {
                        "default": {
                            "description": "An error occurred", "schema": {
                                "$ref": "#/definitions/Error",
                            }
                        },
                        "200": {
                            "description": "My doc string",
                            "schema": {
                                "$ref": "#/definitions/CommandResult",
                            }
                        }
                    },
                    "parameters": [
                        {
                            "in": "header",
                            "name": "X-Response-Skip-Null",
                            "required": False,
                            "type": "string",
                        },
                        {
                            "schema": {
                                "$ref": "#/definitions/CommandArgument",
                            },
                            "name": "body",
                            "in": "body",
                        },
                    ],
                    "operationId": "command",
                }
            }
        })))
