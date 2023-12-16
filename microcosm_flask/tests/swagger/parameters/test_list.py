from hamcrest import assert_that, equal_to, is_
from marshmallow import Schema, fields

from microcosm_flask.fields import QueryStringList
from microcosm_flask.swagger.api import build_parameter


class ForTestSchema(Schema):
    names = fields.List(fields.String)
    qs = QueryStringList(fields.URL)


def test_field_list():
    parameter = build_parameter(ForTestSchema().fields["names"])
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                }
            )
        ),
    )


def test_field_query_string_list():
    parameter = build_parameter(ForTestSchema().fields["qs"])
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "type": "array",
                    "items": {
                        "format": "url",
                        "type": "string",
                    },
                }
            )
        ),
    )
