"""
Test fields.

"""
from enum import Enum, IntEnum, unique

from hamcrest import assert_that, equal_to, has_entries, is_
from marshmallow import Schema

from microcosm_flask.fields import EnumField


@unique
class TestEnum(Enum):
    Foo = "foo"
    Bar = "bar"


@unique
class TestIntEnum(IntEnum):
    Foo = 1
    Bar = 2


class EnumSchema(Schema):
    name = EnumField(TestEnum, by_value=False)
    value = EnumField(TestEnum, by_value=True)
    int_name = EnumField(TestIntEnum, by_value=False)
    int_value = EnumField(TestIntEnum, by_value=True)


def test_load_enums():
    """
    Can deserialize enums.

    """
    schema = EnumSchema()
    result = schema.load({
        "name": TestEnum.Foo.name,
        "value": TestEnum.Bar.value,
        "int_name": TestIntEnum.Foo.name,
        "int_value": TestIntEnum.Bar.value,
    })

    assert_that(result.data["name"], is_(equal_to(TestEnum.Foo)))
    assert_that(result.data["value"], is_(equal_to(TestEnum.Bar)))
    assert_that(result.data["int_name"], is_(equal_to(TestIntEnum.Foo)))
    assert_that(result.data["int_value"], is_(equal_to(TestIntEnum.Bar)))


def test_dump_enums():
    """
    Can serialize enums.

    """
    schema = EnumSchema()
    result = schema.dump({
        "name": TestEnum.Foo,
        "value": TestEnum.Bar,
        "int_name": TestIntEnum.Foo,
        "int_value": TestIntEnum.Bar,
    })

    assert_that(result.data["name"], is_(equal_to(TestEnum.Foo.name)))
    assert_that(result.data["value"], is_(equal_to(TestEnum.Bar.value)))
    assert_that(result.data["int_name"], is_(equal_to(TestIntEnum.Foo.name)))
    assert_that(result.data["int_value"], is_(equal_to(TestIntEnum.Bar.value)))


def test_load_int_enum_as_string():
    """
    Can deserialize int enums from strings.

    """
    schema = EnumSchema()
    result = schema.load({
        "int_value": str(TestIntEnum.Bar.value),
    })

    assert_that(result.data["int_value"], is_(equal_to(TestIntEnum.Bar)))


def test_dump_value_from_string():
    schema = EnumSchema()
    result = schema.dump({
        "name": "foo",
        "value": "bar",
    })

    assert_that(result.data, is_(has_entries(
        name="foo",
        value="bar",
    )))
