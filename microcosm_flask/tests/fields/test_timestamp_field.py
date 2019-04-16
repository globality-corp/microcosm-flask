"""
Test timestamp field.

"""
from hamcrest import (
    assert_that,
    contains,
    equal_to,
    is_,
)
from marshmallow import Schema

from microcosm_flask.fields import TimestampField


TIMESTAMP = 1427702400.0
TIMESTAMP_EXTRA_PRECISION = 1427702400.1
ISOFORMAT_NAIVE = "2015-03-30T08:00:00"
ISOFORMAT_NAIVE_EXTRA_PRECISION = "2015-03-30T08:00:00.100000"
ISOFORMAT_NON_UTC = "2015-03-30T08:00:00+7:00"
ISOFORMAT_UTC = "2015-03-30T08:00:00Z"


class TimestampSchema(Schema):
    unix = TimestampField()
    iso = TimestampField(use_isoformat=True)


def test_load_from_unix_timestamp_float():
    """
    Can deserialize float seconds.

    """
    schema = TimestampSchema()
    result = schema.load({
        "unix": TIMESTAMP,
        "iso": TIMESTAMP,
    })

    assert_that(result.data["unix"], is_(equal_to(TIMESTAMP)))
    assert_that(result.data["iso"], is_(equal_to(TIMESTAMP)))


def test_load_from_unix_timestamp_int():
    """
    Can deserialize int seconds.

    """
    schema = TimestampSchema()
    result = schema.load({
        "unix": int(TIMESTAMP),
        "iso": int(TIMESTAMP),
    })

    assert_that(result.data["unix"], is_(equal_to(int(TIMESTAMP))))
    assert_that(result.data["iso"], is_(equal_to(int(TIMESTAMP))))


def test_load_from_naive_isoformat():
    """
    Can deserialize naive isoformat.

    """
    schema = TimestampSchema()
    result = schema.load({
        "unix": ISOFORMAT_NAIVE,
        "iso": ISOFORMAT_NAIVE,
    })

    assert_that(result.data["unix"], is_(equal_to(TIMESTAMP)))
    assert_that(result.data["iso"], is_(equal_to(TIMESTAMP)))


def test_load_from_naive_isoformat_extra_precision():
    """
    Can deserialize naive isoformat with sub-second precision.

    """
    schema = TimestampSchema()
    result = schema.load({
        "unix": ISOFORMAT_NAIVE_EXTRA_PRECISION,
        "iso": ISOFORMAT_NAIVE_EXTRA_PRECISION,
    })

    assert_that(result.data["unix"], is_(equal_to(TIMESTAMP_EXTRA_PRECISION)))
    assert_that(result.data["iso"], is_(equal_to(TIMESTAMP_EXTRA_PRECISION)))


def test_load_from_utc_isoformat():
    """
    Can deserialize naive isoformat.

    """
    schema = TimestampSchema()
    result = schema.load({
        "unix": ISOFORMAT_UTC,
        "iso": ISOFORMAT_UTC,
    })

    assert_that(result.data["unix"], is_(equal_to(TIMESTAMP)))
    assert_that(result.data["iso"], is_(equal_to(TIMESTAMP)))


def test_load_from_non_utc_isoformat():
    """
    Can deserialize naive isoformat.

    """
    schema = TimestampSchema()
    result = schema.load({
        "unix": ISOFORMAT_NON_UTC,
        "iso": ISOFORMAT_NON_UTC,
    })

    assert_that(result.errors["unix"], contains("Timestamps must be defined in UTC"))
    assert_that(result.errors["iso"], contains("Timestamps must be defined in UTC"))


def test_dump():
    """
    Can serialize to appropriate type.

    """
    schema = TimestampSchema()
    result = schema.dump({
        "unix": TIMESTAMP,
        "iso": TIMESTAMP,
    })

    assert_that(result.data["unix"], is_(equal_to(TIMESTAMP)))
    assert_that(result.data["iso"], is_(equal_to(ISOFORMAT_NAIVE)))
