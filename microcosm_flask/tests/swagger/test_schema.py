"""
Test JSON Schema generation.

"""
from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from enum import Enum, IntEnum, unique
from marshmallow import Schema, fields

from microcosm_flask.fields import (
    EnumField,
    TimestampField,
)
from microcosm_flask.swagger.schema import (
    build_schema,
    build_parameter,
    swagger_field,
)
from microcosm_flask.tests.conventions.fixtures import NewPersonSchema


class MixedField(fields.Field):
    __swagger_type__ = ["integer", "string"]


@unique
class Choices(Enum):
    Profit = "profit"


@unique
class ValueType(IntEnum):
    Foo = 1
    Bar = 2


class TestSchema(Schema):
    id = fields.UUID()
    foo = fields.String(description="Foo", default="bar")
    choice = EnumField(Choices)
    value = EnumField(ValueType, by_value=True)
    names = fields.List(fields.String)
    payload = fields.Dict()
    ref = fields.Nested(NewPersonSchema)
    decimal = fields.Decimal()
    decimalString = fields.Decimal(as_string=True)
    decorated = swagger_field(fields.Method())
    datetime = fields.DateTime()
    unix_timestamp = TimestampField()
    iso_timestamp = TimestampField(use_isoformat=True)
    mixed = MixedField()


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
        },
        "required": [
            "firstName",
            "lastName",
        ],
    })))


def test_field_description_and_default():
    parameter = build_parameter(TestSchema().fields["foo"])
    assert_that(parameter, is_(equal_to({
        "type": "string",
        "description": "Foo",
        "default": "bar",
    })))


def test_field_format():
    parameter = build_parameter(TestSchema().fields["id"])
    assert_that(parameter, is_(equal_to({
        "type": "string",
        "format": "uuid",
    })))


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


def test_field_array():
    parameter = build_parameter(TestSchema().fields["names"])
    assert_that(parameter, is_(equal_to({
        "type": "array",
        "items": {
            "type": "string",
        }
    })))


def test_field_decimal():
    parameter = build_parameter(TestSchema().fields["decimal"])
    assert_that(parameter, is_(equal_to({
        "type": "number",
    })))


def test_field_decimal_as_string():
    parameter = build_parameter(TestSchema().fields["decimalString"])
    assert_that(parameter, is_(equal_to({
        "type": "string",
        "format": "decimal",
    })))


def test_field_dict():
    parameter = build_parameter(TestSchema().fields["payload"])
    assert_that(parameter, is_(equal_to({
        "type": "object",
    })))


def test_field_nested():
    parameter = build_parameter(TestSchema().fields["ref"])
    assert_that(parameter, is_(equal_to({
        "$ref": "#/definitions/NewPerson",
    })))


def test_field_decorated_method():
    parameter = build_parameter(TestSchema().fields["decorated"])
    assert_that(parameter, is_(equal_to({
        # NB: default for `fields.Method` is "object"
        "type": "string",
    })))


def test_field_datetime():
    parameter = build_parameter(TestSchema().fields["datetime"])
    assert_that(parameter, is_(equal_to({
        "type": "string",
        "format": "date-time",
    })))


def test_field_unix_timestamp():
    parameter = build_parameter(TestSchema().fields["unix_timestamp"])
    assert_that(parameter, is_(equal_to({
        "type": "float",
        "format": "timestamp",
    })))


def test_field_iso_timestamp():
    parameter = build_parameter(TestSchema().fields["iso_timestamp"])
    assert_that(parameter, is_(equal_to({
        "type": "string",
        "format": "date-time",
    })))


def test_field_one_of():
    parameter = build_parameter(TestSchema().fields["mixed"])
    assert_that(parameter, is_(equal_to({
        "oneOf": [
            {
                "type": "integer",
            },
            {
                "type": "string",
            }
        ],
    })))
