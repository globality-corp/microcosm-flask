from enum import Enum, IntEnum, unique

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


class TestSchema(Schema):
    choice = EnumField(Choices)
    value = EnumField(ValueType, by_value=True)


def test_field_enum():
    parameter = build_parameter(TestSchema().fields["choice"])
    assert_that(parameter, is_(equal_to({
        "type": "string",
        "enum": [
            "Profit",
        ],
    })))


def test_field_int_enum():
    parameter = build_parameter(TestSchema().fields["value"])
    assert_that(parameter, is_(equal_to({
        "type": "integer",
        "enum": [
            1,
            2
        ],
    })))
