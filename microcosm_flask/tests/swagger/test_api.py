"""
Test JSON Schema generation.

"""
from hamcrest import assert_that, equal_to, is_

from microcosm_flask.swagger.api import build_schema, iter_schemas
from microcosm_flask.tests.conventions.fixtures import NewPersonSchema, RecursiveSchema


def test_schema_generation():
    schema = build_schema(NewPersonSchema())
    assert_that(schema, is_(equal_to({
        "type": "object",
        "properties": {
            "eyeColor": {
                "enum": [
                    "PURPLE",
                    "TEAL",
                    "RUBY",
                ],
                "format": "enum",
                "type": "string",
            },
            "firstName": {
                "type": "string",
            },
            "lastName": {
                "type": "string",
            },
            "email": {
                "format": "email",
                "type": "string",
            },
        },
        "required": [
            "firstName",
            "lastName",
        ],
    })))


def test_schema_generation_non_strict_enums():
    schema = build_schema(NewPersonSchema(), strict_enums=False)
    assert_that(schema, is_(equal_to({
        "type": "object",
        "properties": {
            "eyeColor": {
                "type": "string",
            },
            "firstName": {
                "type": "string",
            },
            "lastName": {
                "type": "string",
            },
            "email": {
                "format": "email",
                "type": "string",
            },
        },
        "required": [
            "firstName",
            "lastName",
        ],
    })))


def test_schema_generation_recursive():
    # BEWARE: Using `next` instead of `list()[0]` here wouldn't actually test
    # what we want, because it would just grab the first item and not trigger
    # the infinite recursion.
    schemas = list(iter_schemas(RecursiveSchema()))
    name, schema = schemas[0]
    assert_that(schema, is_(equal_to({
        "type": "object",
        "properties": {'children': {
            'type': 'array',
            'items': {'$ref': '#/definitions/Recursive'},
        }},
    })))
