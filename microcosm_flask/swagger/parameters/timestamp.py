from marshmallow.fields import Field

from microcosm_flask.fields import TimestampField
from microcosm_flask.swagger.parameters.base import ParameterBuilder


class TimestampParameterBuilder(ParameterBuilder):
    """
    Build a timestamp parameter.

    """
    def supports_field(self, field: Field) -> bool:
        return isinstance(field, TimestampField)

    def parse_format(self, field: Field) -> str:
        if isinstance(field, TimestampField) and field.use_isoformat:
            return "date-time"
        return "timestamp"

    def parse_type(self, field: Field) -> str:
        if isinstance(field, TimestampField) and field.use_isoformat:
            return "string"
        return "float"
