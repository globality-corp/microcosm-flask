from hamcrest import assert_that, equal_to, is_
from marshmallow import Schema, fields

from microcosm_flask.swagger.api import build_parameter


class TestSchema(Schema):
    deprecated_constant_list = fields.Constant(constant=[], dump_only=True)
    deprecated_constant_string = fields.Constant(constant="HELLO", dump_only=True)
    deprecated_constant_int = fields.Constant(constant=123, dump_only=True)



def test_field_constant_list():
    parameter = build_parameter(TestSchema().fields["deprecated_constant_list"])
    assert_that(parameter, is_(equal_to({
        "type": "array",
    })))

def test_field_constant_string():
    parameter = build_parameter(TestSchema().fields["deprecated_constant_string"])
    assert_that(parameter, is_(equal_to({
        "type": "string",
        "default": "HELLO",
    })))

def test_field_constant_int():
    parameter = build_parameter(TestSchema().fields["deprecated_constant_int"])
    assert_that(parameter, is_(equal_to({
        "type": "integer",
        "default": 123,
    })))
