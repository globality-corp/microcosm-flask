"""
Test fields.

"""
import re
from enum import Enum, IntEnum, unique

from hamcrest import (
    assert_that,
    calling,
    contains_exactly,
    equal_to,
    has_properties,
    is_,
    raises,
)
from marshmallow import Schema, ValidationError
from werkzeug.datastructures import ImmutableMultiDict

from microcosm_flask.fields import EnumField, QueryStringList
from microcosm_flask.fields.order_by_field import OrderBy, OrderByField, OrderDirection


@unique
class ForTestEnum(Enum):
    Foo = "foo"
    Bar = "bar"


@unique
class ForTestIntEnum(IntEnum):
    Foo = 1
    Bar = 2


class OrderFieldSchema(Schema):
    order_by_str = OrderByField(enum_field=EnumField(ForTestEnum))
    order_by_int = OrderByField(enum_field=EnumField(ForTestIntEnum))
    order_by_str_field_list = QueryStringList(OrderByField(enum_field=EnumField(ForTestEnum)))
    order_by_int_field_list = QueryStringList(OrderByField(enum_field=EnumField(ForTestIntEnum)))


def test_load_order_by():
    """
    Can deserialize enums.

    """
    schema = OrderFieldSchema()

    result = schema.load(
        ImmutableMultiDict(
            [
                (
                    "order_by_str",
                    f"+{ForTestEnum.Foo.name}"
                ),
                (
                    "order_by_int",
                    f"-{ForTestIntEnum.Bar.name}"
                ),
                (
                    "order_by_str_field_list",
                    f"+{ForTestEnum.Foo.name},-{ForTestEnum.Bar.name},{ForTestEnum.Bar.name}"
                ),
                (
                    "order_by_int_field_list",
                    f"+{ForTestIntEnum.Foo.name},-{ForTestIntEnum.Bar.name},{ForTestIntEnum.Bar.name}"
                )
            ]
        ),
    )

    assert_that(result["order_by_str"], has_properties(order_field=ForTestEnum.Foo, order_dir=OrderDirection.ASC))
    assert_that(result["order_by_int"], has_properties(order_field=ForTestIntEnum.Bar, order_dir=OrderDirection.DESC)),
    assert_that(result["order_by_str_field_list"], contains_exactly(
            has_properties(order_field=ForTestEnum.Foo, order_dir=OrderDirection.ASC),
            has_properties(order_field=ForTestEnum.Bar, order_dir=OrderDirection.DESC),
            has_properties(order_field=ForTestEnum.Bar, order_dir=OrderDirection.ASC),
        ),
    )
    assert_that(result["order_by_int_field_list"], contains_exactly(
            has_properties(order_field=ForTestIntEnum.Foo, order_dir=OrderDirection.ASC),
            has_properties(order_field=ForTestIntEnum.Bar, order_dir=OrderDirection.DESC),
            has_properties(order_field=ForTestIntEnum.Bar, order_dir=OrderDirection.ASC),
        ),
    )


def test_dumop_order_by():
    """
    Can serialize enums.

    """
    schema = OrderFieldSchema()
    result = schema.dump(
        {
            "order_by_str": OrderBy(ForTestEnum.Foo, OrderDirection.ASC),
            "order_by_int": OrderBy(ForTestIntEnum.Bar, OrderDirection.DESC),
            "order_by_str_field_list": [
                OrderBy(ForTestEnum.Foo, OrderDirection.ASC),
                OrderBy(ForTestEnum.Bar, OrderDirection.DESC),
                OrderBy(ForTestEnum.Bar, OrderDirection.ASC),
            ],
            "order_by_int_field_list": [
                OrderBy(ForTestIntEnum.Foo, OrderDirection.ASC),
                OrderBy(ForTestIntEnum.Bar, OrderDirection.DESC),
                OrderBy(ForTestIntEnum.Bar, OrderDirection.ASC),
            ],
        }
    )

    assert_that(result["order_by_str"], is_(equal_to(f"+{ForTestEnum.Foo.name}")))
    assert_that(result["order_by_int"], is_(equal_to(f"-{ForTestIntEnum.Bar.name}")))
    # assert_that(result["order_by_str_field_list"], is_(equal_to(
    #     f"+{ForTestEnum.Foo.name},-{ForTestEnum.Bar.name},{ForTestEnum.Bar.name}"
    # )))
    # assert_that(result["order_by_int_field_list"], is_(equal_to(
    #     f"+{ForTestIntEnum.Foo.name},-{ForTestIntEnum.Bar.name},{ForTestIntEnum.Bar.name}"
    # )))


def test_invalid_args():
    """
    Can deserialize enums.

    """
    schema = OrderFieldSchema()

    assert_that(
        calling(schema.load).with_args(
            ImmutableMultiDict(
                [
                    (
                        "order_by_str",
                        "+INVALID_ENUM"
                    ),
                ]
            )
        ),
        raises(ValidationError, pattern=re.escape("{'order_by_str': ['Invalid enum member INVALID_ENUM']}")),
    )
