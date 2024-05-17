from hamcrest import assert_that, equal_to, is_
from marshmallow import Schema, fields

from microcosm_flask.swagger.api import build_parameter
from microcosm_flask.swagger.decorators import swagger_field


class MixedField(fields.Field):
    __swagger_type__ = ["integer", "string"]


class FooSchema(Schema):
    decorated = swagger_field(swagger_format="uuid")(
        fields.Method(),
    )
    mixed = MixedField()


def test_field_decorated():
    parameter = build_parameter(FooSchema().fields["decorated"])
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "type": "string",
                    "format": "uuid",
                }
            )
        ),
    )


def test_field_one_of():
    parameter = build_parameter(FooSchema().fields["mixed"])
    assert_that(parameter, is_(equal_to({})))
