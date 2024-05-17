from hamcrest import assert_that, equal_to, is_
from marshmallow import Schema, fields

from microcosm_flask.swagger.api import build_parameter
from microcosm_flask.tests.conventions.fixtures import NewPersonSchema


class FooSchema(Schema):
    ref = fields.Nested(NewPersonSchema)


def test_field_nested():
    parameter = build_parameter(FooSchema().fields["ref"])
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "$ref": "#/definitions/NewPerson",
                }
            )
        ),
    )
