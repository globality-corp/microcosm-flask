"""
Test fields.

"""
from enum import Enum, IntEnum, unique

from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_entries,
    is_,
    raises,
)
from marshmallow import Schema, ValidationError

from microcosm_flask.fields import EnumField


@unique
class ForTestEnum(Enum):
    Foo = "foo"
    Bar = "bar"


@unique
class ForTestIntEnum(IntEnum):
    Foo = 1
    Bar = 2


class EnumSchema(Schema):
    name = EnumField(ForTestEnum, by_value=False)
    value = EnumField(ForTestEnum, by_value=True)
    int_name = EnumField(ForTestIntEnum, by_value=False)
    int_value = EnumField(ForTestIntEnum, by_value=True)


def test_load_enums():
    """
    Can deserialize enums.

    """
    schema = EnumSchema()
    result = schema.load(
        {
            "name": ForTestEnum.Foo.name,
            "value": ForTestEnum.Bar.value,
            "int_name": ForTestIntEnum.Foo.name,
            "int_value": ForTestIntEnum.Bar.value,
        }
    )

    assert_that(result["name"], is_(equal_to(ForTestEnum.Foo)))
    assert_that(result["value"], is_(equal_to(ForTestEnum.Bar)))
    assert_that(result["int_name"], is_(equal_to(ForTestIntEnum.Foo)))
    assert_that(result["int_value"], is_(equal_to(ForTestIntEnum.Bar)))


def test_dump_enums():
    """
    Can serialize enums.

    """
    schema = EnumSchema()
    result = schema.dump(
        {
            "name": ForTestEnum.Foo,
            "value": ForTestEnum.Bar,
            "int_name": ForTestIntEnum.Foo,
            "int_value": ForTestIntEnum.Bar,
        }
    )

    assert_that(result["name"], is_(equal_to(ForTestEnum.Foo.name)))
    assert_that(result["value"], is_(equal_to(ForTestEnum.Bar.value)))
    assert_that(result["int_name"], is_(equal_to(ForTestIntEnum.Foo.name)))
    assert_that(result["int_value"], is_(equal_to(ForTestIntEnum.Bar.value)))


def test_load_int_enum_as_string():
    """
    Can deserialize int enums from strings.

    """
    schema = EnumSchema()
    result = schema.load(
        {
            "int_value": str(ForTestIntEnum.Bar.value),
        }
    )

    assert_that(result["int_value"], is_(equal_to(ForTestIntEnum.Bar)))


def test_dump_value_from_string():
    schema = EnumSchema()
    result = schema.dump(
        {
            "name": "foo",
            "value": "bar",
        }
    )

    assert_that(
        result,
        is_(
            has_entries(
                name="foo",
                value="bar",
            )
        ),
    )


def test_load_invalid():
    schema = EnumSchema()
    assert_that(
        calling(schema.load).with_args(
            dict(
                name="unknown",
            )
        ),
        raises(ValidationError),
    )
