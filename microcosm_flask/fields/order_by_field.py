from enum import Enum

from marshmallow import fields

from microcosm_flask.fields import EnumField


class OrderDirection(Enum):
    ASC = "+"
    DESC = "-"


class OrderBy:

    def __init__(self, order_field: Enum, order_dir: OrderDirection):
        self.order_field = order_field
        self.order_dir = order_dir

    def __str__(self):
        # This is used when serializing the object to a string for the URL. It doesn't actually use the _serialize
        # method below.
        return self.order_dir.value + self.order_field.name


class OrderByField(fields.Str):
    """
    OrderByField valued field. Allow for sorting by a set of fields and directions. Most use cases will wrap the field
    within a QueryStringList field to allow for multiple values, but it is not required. The field requires setting
    the enum field parameter to allow for users to create their own enum types to use for sorting.

    Example:
        the url /articles?sort=-created,title

        will create a sort field with two OrderBy entries:
        - OrderBy(created, OrderDirection.DESC)
        - OrderBy(title, OrderDirection.ASC)

        Note that in this example, Title does not have a +/-. This will give the field a default of sort ASC. This is
        all in accordance with the JSON API standard.

    JSON API standard: https://jsonapi.org/format/1.1/#fetching-sorting
    """

    def __init__(self, enum_field, *args, **kwargs):
        self.enum_field: EnumField = enum_field
        super().__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        # Just return the __str__ from above
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):
        if value.startswith(OrderDirection.DESC.value):
            direction = OrderDirection.DESC
            parsed_value = value[1:]
        elif value.startswith(OrderDirection.ASC.value):
            direction = OrderDirection.ASC
            parsed_value = value[1:]
        else:
            direction = OrderDirection.ASC
            parsed_value = value
        validated_value = self.enum_field.deserialize(parsed_value, attr, data, **kwargs)
        return OrderBy(validated_value, direction)
