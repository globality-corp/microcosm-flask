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
class FooEnum(Enum):
    Foo = "foo"
    Bar = "bar"


@unique
class FooIntEnum(IntEnum):
    Foo = 1
    Bar = 2


class EnumSchema(Schema):
    name = EnumField(FooEnum, by_value=False)
    value = EnumField(FooEnum, by_value=True)
    int_name = EnumField(FooIntEnum, by_value=False)
    int_value = EnumField(FooIntEnum, by_value=True)


def test_load_enums():
    """
    Can deserialize enums.

    """
    schema = EnumSchema()
    result = schema.load({
        "name": FooEnum.Foo.name,
        "value": FooEnum.Bar.value,
        "int_name": FooIntEnum.Foo.name,
        "int_value": FooIntEnum.Bar.value,
    })

    assert_that(result["name"], is_(equal_to(FooEnum.Foo)))
    assert_that(result["value"], is_(equal_to(FooEnum.Bar)))
    assert_that(result["int_name"], is_(equal_to(FooIntEnum.Foo)))
    assert_that(result["int_value"], is_(equal_to(FooIntEnum.Bar)))


def test_dump_enums():
    """
    Can serialize enums.

    """
    schema = EnumSchema()
    result = schema.dump({
        "name": FooEnum.Foo,
        "value": FooEnum.Bar,
        "int_name": FooIntEnum.Foo,
        "int_value": FooIntEnum.Bar,
    })

    assert_that(result["name"], is_(equal_to(FooEnum.Foo.name)))
    assert_that(result["value"], is_(equal_to(FooEnum.Bar.value)))
    assert_that(result["int_name"], is_(equal_to(FooIntEnum.Foo.name)))
    assert_that(result["int_value"], is_(equal_to(FooIntEnum.Bar.value)))


def test_load_int_enum_as_string():
    """
    Can deserialize int enums from strings.

    """
    schema = EnumSchema()
    result = schema.load({
        "int_value": str(FooIntEnum.Bar.value),
    })

    assert_that(result["int_value"], is_(equal_to(FooIntEnum.Bar)))


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
