"""
Test Swagger definition construction.

"""
from hamcrest import assert_that, equal_to, has_entries
from microcosm.api import create_object_graph
from microcosm.loaders import load_from_dict

from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.conventions.registry import iter_endpoints
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation
from microcosm_flask.swagger.definitions import build_swagger
from microcosm_flask.tests.conventions.fixtures import (
    NewPersonSchema,
    Person,
    PersonSchema,
    UpdatePersonSchema,
    person_create,
    person_update,
)


PERSON_MAPPINGS = {
    Operation.Create: (person_create, NewPersonSchema(), PersonSchema()),
    Operation.Update: (person_update, UpdatePersonSchema(), PersonSchema()),
}


# match all (of the one) operations
def match_function(operation, obj, rule):
    return True


def test_build_swagger():
    graph = create_object_graph(name="example", testing=True)
    ns = Namespace(
        subject=Person,
        version="v1",
    )
    configure_crud(graph, ns, PERSON_MAPPINGS)

    with graph.flask.test_request_context():
        operations = list(iter_endpoints(graph, match_function))
        swagger_schema = build_swagger(graph, ns, operations)

    assert_that(swagger_schema, has_entries(
        info={
            "version": "v1",
            "title": "example",
        },
        paths={
            "/person": {
                "post": {
                    "tags": ["person"],
                    "responses": {
                        "default": {
                            "description": "An error occurred", "schema": {
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
                            "in": "header",
                            "name": "X-Response-Skip-Null",
                            "required": False,
                            "type": "string",
                        },
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
                            "description": "An error occurred",
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
                            "required": False,
                            "type": "string",
                            "name": "X-Response-Skip-Null",
                            "in": "header",
                        },
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {
                                "$ref": "#/definitions/UpdatePerson",
                            },
                        },
                        {
                            "required": True,
                            "type": "string",
                            "name": "person_id",
                            "in": "path",
                            "format": "uuid",
                        },
                    ],
                    "operationId": "update",
                },
            },
        },
        produces=[
            "application/json",
        ],
        definitions=has_entries(
            NewPerson=has_entries(
                required=[
                    "firstName",
                    "lastName",
                ],
                type="object",
                properties={
                    "email": {
                        "type": "string",
                        "format": "email",
                    },
                    "lastName": {
                        "type": "string",
                    },
                    "firstName": {
                        "type": "string",
                    }
                }
            ),
            Person=has_entries(
                required=[
                    "firstName",
                    "id",
                    "lastName",
                ],
                type="object",
                properties={
                    "email": {
                        "type": "string",
                        "format": "email",
                    },
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
            ),
            PersonPubsubMessage=has_entries(
                type="object",
                properties={
                    "email": {
                        "format": "email",
                        "type": "string",
                    },
                    "firstName": {
                        "type": "string",
                    },
                },
                required=[
                    "email",
                    "firstName",
                ],
            ),
            PersonFoo=has_entries(
                type="object",
                properties={
                    "email": {
                        "format": "email",
                        "type": "string",
                    },
                    "firstName": {
                        "type": "string",
                    },
                },
                required=[
                    "email",
                ],
            ),
            UpdatePerson=dict(
                type="object",
                properties={
                    "lastName": {
                        "type": "string",
                    },
                    "firstName": {
                        "type": "string",
                    }
                }
            ),
            ErrorContext=has_entries(
                required=["errors"],
                type="object",
                properties={
                    "errors": {
                        "items": {
                            "$ref": "#/definitions/SubError",
                        },
                        "type": "array",
                    },
                },
            ),
            SubError=has_entries(
                required=["message"],
                type="object",
                properties={
                    "message": {
                        "type": "string",
                    },
                },
            ),
            Error=has_entries(
                required=[
                    "code",
                    "message",
                    "retryable",
                ],
                type="object",
                properties={
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
            ),
        ),
        basePath="/api/v1",
        swagger="2.0",
        consumes=[
            "application/json",
        ],
    ))


def test_no_prefix_no_version_path():
    loader = load_from_dict(dict(
        # We want our routes to come directly after the root /
        build_route_path=dict(
            prefix=""
        ),
    ))
    graph = create_object_graph(name="example", testing=True, loader=loader)

    ns = Namespace(
        subject=Person,
        version="",
    )
    configure_crud(graph, ns, PERSON_MAPPINGS)

    with graph.flask.test_request_context():
        operations = list(iter_endpoints(graph, match_function))
        swagger_schema = build_swagger(graph, ns, operations)

    # Test that in a no prefix, no version case we still get a leading slash in our paths
    assert_that("/person" in swagger_schema["paths"])
    assert_that(swagger_schema["basePath"], equal_to("/"))
