"""
Test Swagger definition construction.

"""
from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm.api import create_object_graph
from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.operations import Operation
from microcosm_flask.conventions.registry import iter_endpoints
from microcosm_flask.namespaces import Namespace
from microcosm_flask.swagger.definitions import build_swagger
from microcosm_flask.tests.conventions.fixtures import (
    NewPersonSchema,
    person_create,
    person_update,
    Person,
    PersonSchema,
    UpdatePersonSchema,
)


PERSON_MAPPINGS = {
    Operation.Create: (person_create, NewPersonSchema(), PersonSchema()),
    Operation.Update: (person_update, UpdatePersonSchema(), PersonSchema()),
}


def test_build_swagger():
    graph = create_object_graph(name="example", testing=True)
    ns = Namespace(
        subject=Person,
        version="v1",
    )
    configure_crud(graph, ns.subject, PERSON_MAPPINGS, ns.path)

    # match all (of the one) operations
    def match_function(operation, obj, rule):
        return True

    with graph.flask.test_request_context():
        operations = list(iter_endpoints(graph, match_function))
        swagger_schema = build_swagger(graph, ns, operations)

    assert_that(swagger_schema, is_(equal_to({
        "info": {
            "version": "v1",
            "title": "example",
        },
        "paths": {
            "/person": {
                "post": {
                    "tags": ["person"],
                    "responses": {
                        "default": {
                            "description": "An error occcurred", "schema": {
                                "$ref": "#/definitions/Error",
                            }
                        },
                        "201": {
                            "description": "Create a new person",
                            "schema": {
                                "$ref": "#/definitions/Person",
                            },
                        },
                    },
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {
                                "$ref": "#/definitions/NewPerson",
                            },
                        },
                    ],
                    "operationId": "create",
                },
            },
            "/person/{person_id}": {
                "patch": {
                    "tags": ["person"],
                    "responses": {
                        "default": {
                            "description": "An error occcurred",
                            "schema": {
                                "$ref": "#/definitions/Error",
                            },
                        },
                        "200": {
                            "description": "Update some or all of a person by id",
                            "schema": {
                                "$ref": "#/definitions/Person",
                            },
                        },
                    },
                    "parameters": [
                        {
                            "required": True,
                            "type": "string",
                            "name": "person_id",
                            "in": "path",
                        },
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {
                                "$ref": "#/definitions/UpdatePerson",
                            },
                        },
                    ],
                    "operationId": "update",
                },
            },
        },
        "produces": [
            "application/json",
        ],
        "definitions": {
            "NewPerson": {
                "required": [
                    "firstName",
                    "lastName",
                ],
                "type": "object",
                "properties": {
                    "lastName": {
                        "type": "string",
                    },
                    "firstName": {
                        "type": "string",
                    }
                }
            },
            "Person": {
                "required": [
                    "firstName",
                    "id",
                    "lastName",
                ],
                "type": "object",
                "properties": {
                    "lastName": {
                        "type": "string",
                    },
                    "_links": {
                        "type": "object"
                    },
                    "id": {
                        "type": "string",
                        "format": "uuid",
                    },
                    "firstName": {
                        "type": "string",
                    },
                },
            },
            "UpdatePerson": {
                "type": "object",
                "properties": {
                    "lastName": {
                        "type": "string",
                    },
                    "firstName": {
                        "type": "string",
                    }
                }
            },
            "ErrorContext": {
                "required": ["errors"],
                "type": "object",
                "properties": {
                    "errors": {
                        "items": {
                            "$ref": "#/definitions/SubError",
                        },
                        "type": "array",
                    },
                },
            },
            "SubError": {
                "required": ["message"],
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                    },
                },
            },
            "Error": {
                "required": [
                    "code",
                    "message",
                    "retryable",
                ],
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "default": "Unknown Error",
                    },
                    "code": {
                        "type": "integer",
                        "format": "int32",
                        "default": 500,
                    },
                    "context": {
                        "$ref": "#/definitions/ErrorContext",
                    },
                    "retryable": {
                        "type": "boolean",
                    },
                },
            },
        },
        "basePath": "/api/v1",
        "swagger": "2.0",
        "consumes": [
            "application/json",
        ],
    })))
