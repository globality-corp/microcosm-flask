"""
Test JSON Schema generation.

"""
from hamcrest import assert_that, equal_to, is_

from microcosm_flask.swagger.api import build_schema
from microcosm_flask.tests.conventions.fixtures import NewPersonSchema


def test_schema_generation():
    schema = build_schema(NewPersonSchema())
    assert_that(schema, is_(equal_to({
        "type": "object",
        "properties": {
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
