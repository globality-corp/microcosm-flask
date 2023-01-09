from hamcrest import assert_that, equal_to, is_
from marshmallow import Schema, fields

from microcosm_flask.swagger.api import build_parameter


class TestSchema(Schema):
    id = fields.UUID()
    foo = fields.String(metadata={"description": "Foo"}, dump_default="bar")
    payload = fields.Dict()
    datetime = fields.DateTime()


def test_field_description_and_default():
    parameter = build_parameter(TestSchema().fields["foo"])
    assert_that(parameter, is_(equal_to({
        "type": "string",
        "description": "Foo",
        "default": "bar",
    })))


def test_field_uuid():
    parameter = build_parameter(TestSchema().fields["id"])
    assert_that(parameter, is_(equal_to({
        "type": "string",
        "format": "uuid",
    })))


def test_field_dict():
    parameter = build_parameter(TestSchema().fields["payload"])
    assert_that(parameter, is_(equal_to({
        "type": "object",
    })))
