from hamcrest import assert_that, equal_to, is_
from marshmallow import Schema, fields

from microcosm_flask.swagger.api import build_parameter


class ForTestSchema(Schema):
    id = fields.UUID()
    foo = fields.String(metadata={"description": "Foo"}, default="bar")
    payload = fields.Dict()
    datetime = fields.DateTime()


def test_field_description_and_default():
    parameter = build_parameter(ForTestSchema().fields["foo"])
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "type": "string",
                    "description": "Foo",
                    "default": "bar",
                }
            )
        ),
    )


def test_field_uuid():
    parameter = build_parameter(ForTestSchema().fields["id"])
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


def test_field_dict():
    parameter = build_parameter(ForTestSchema().fields["payload"])
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "type": "object",
                }
            )
        ),
    )
