"""
A list field field that supports query string parameter parsing.

"""
from marshmallow.fields import List, ValidationError


class QueryStringList(List):
    def _deserialize(self, value, attr, obj):
        """
        _deserialize handles multiple formats of query string parameter lists
        including:

        /foo?bars=1,2
        /foo?bars[]=1&bars[]2

        and returns a list of values

        """
        if value is None:
            return None

        try:
            attribute_elements = [attr_element.split(",") for attr_element in obj.getlist(attr)]
            attribute_params = [param for attr_param in attribute_elements for param in attr_param]

            return attribute_params
        except ValueError:
            raise ValidationError("Invalid query string list argument")

    def _serialize(self, value, attr, obj):
        return ",".join(str(val) for val in super(QueryStringList, self)._serialize(value, attr, obj))
