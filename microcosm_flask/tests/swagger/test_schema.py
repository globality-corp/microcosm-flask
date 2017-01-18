"""
Test JSON Schema generation.

"""
from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    is_,
    not_,
)

from enum import Enum, IntEnum, unique
from marshmallow import Schema, fields

from microcosm_flask.fields import EnumField
from microcosm_flask.swagger.schema import build_schema, build_parameter
from microcosm_flask.tests.conventions.fixtures import NewPersonSchema


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
    bar = fields.String(allow_none=True, required=True)
    baz = fields.String(allow_none=True, required=False)
    choice = EnumField(Choices)
    value = EnumField(ValueType, by_value=True)
    names = fields.List(fields.String)
    payload = fields.Dict()
    ref = fields.Nested(NewPersonSchema)
    decimal = fields.Decimal()
    decimalString = fields.Decimal(as_string=True)


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
    })))


def test_field_dict():
    parameter = build_parameter(TestSchema().fields["payload"])
    assert_that(parameter, is_(equal_to({
        "type": "object",
    })))


def test_required_field_allow_none():
    parameter = build_parameter(TestSchema().fields["bar"])
    schema = build_schema(TestSchema())
    assert_that(parameter, is_(equal_to({
        "type": "string",
        "x-nullable": True,
    })))
    assert_that(schema, has_entries(
        required=["bar"]
    ))


def test_non_required_field_allow_none():
    parameter = build_parameter(TestSchema().fields["baz"])
    schema = build_schema(TestSchema())
    assert_that(parameter, is_(equal_to({
        "type": "string",
        "x-nullable": True,
    })))
    assert_that(schema, not_(has_entries(
        required=["baz"]
    )))


def test_field_nested():
    parameter = build_parameter(TestSchema().fields["ref"])
    assert_that(parameter, is_(equal_to({
        "$ref": "#/definitions/NewPerson",
    })))
