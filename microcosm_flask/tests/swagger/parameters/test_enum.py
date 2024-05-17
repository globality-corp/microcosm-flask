from enum import (
    Enum,
    EnumMeta,
    IntEnum,
    unique,
)

from hamcrest import assert_that, equal_to, is_
from marshmallow import Schema

from microcosm_flask.fields import EnumField
from microcosm_flask.swagger.api import build_parameter


@unique
class Choices(Enum):
    Profit = "profit"


@unique
class ValueType(IntEnum):
    Foo = 1
    Bar = 2


class FormatNonStrictMeta(EnumMeta):
    __openapi_strict__ = False


@unique
class ChoicesNonStrict(Enum, metaclass=FormatNonStrictMeta):
    Profit = "profit"


class FooSchema(Schema):
    choice = EnumField(Choices)
    value = EnumField(ValueType, by_value=True)
    choice_non_strict = EnumField(ChoicesNonStrict)


def test_field_enum():
    parameter = build_parameter(FooSchema().fields["choice"])
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "format": "enum",
                    "type": "string",
                    "enum": [
                        "Profit",
                    ],
                }
            )
        ),
    )


def test_field_enum_non_strict():
    parameter = build_parameter(FooSchema().fields["choice"], strict_enums=False)
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "type": "string",
                }
            )
        ),
    )


def test_field_int_enum():
    parameter = build_parameter(FooSchema().fields["value"])
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "format": "enum",
                    "type": "integer",
                    "enum": [1, 2],
                }
            )
        ),
    )


def test_enum_format_override():
    parameter = build_parameter(FooSchema().fields["choice_non_strict"])
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "type": "string",
                }
            )
        ),
    )
