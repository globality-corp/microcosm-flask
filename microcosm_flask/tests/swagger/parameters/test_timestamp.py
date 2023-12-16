from hamcrest import assert_that, equal_to, is_
from marshmallow import Schema

from microcosm_flask.fields import TimestampField
from microcosm_flask.swagger.api import build_parameter


class ForTestSchema(Schema):
    unix_timestamp = TimestampField()
    iso_timestamp = TimestampField(use_isoformat=True)


def test_field_unix_timestamp():
    parameter = build_parameter(ForTestSchema().fields["unix_timestamp"])
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "type": "float",
                    "format": "timestamp",
                }
            )
        ),
    )


def test_field_iso_timestamp():
    parameter = build_parameter(ForTestSchema().fields["iso_timestamp"])
    assert_that(
        parameter,
        is_(
            equal_to(
                {
                    "type": "string",
                    "format": "date-time",
                }
            )
        ),
    )
