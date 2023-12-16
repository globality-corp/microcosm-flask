from hamcrest import assert_that, equal_to, is_
from marshmallow import Schema, fields

from microcosm_flask.swagger.api import build_parameter


class ForTestSchema(Schema):
    decimal = fields.Decimal()
    decimalString = fields.Decimal(as_string=True)


def test_field_decimal():
    parameter = build_parameter(ForTestSchema().fields["decimal"])
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "type": "number",
                }
            )
        ),
    )


def test_field_decimal_as_string():
    parameter = build_parameter(ForTestSchema().fields["decimalString"])
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "type": "string",
                    "format": "decimal",
                }
            )
        ),
    )
