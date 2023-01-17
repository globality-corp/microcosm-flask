from typing import Any, Mapping

from marshmallow.fields import Field, Constant

from microcosm_flask.swagger.parameters.base import ParameterBuilder
from microcosm_flask.swagger.parameters.enum import is_int


class ConstantParameterBuilder(ParameterBuilder):
    """
    Builder parameters for constant fields.

    """
    def supports_field(self, field: Field) -> bool:
        return isinstance(field, Constant)

    def parse_default(self, field: Constant) -> Any:
        """
        Parse the default value for the field, if any.

        """
        return field.constant

    def parse_type(self, field: Constant) -> str:
        if isinstance(field.constant, list):
            return "array"
        elif isinstance(field.constant, str):
            return "string"
        elif is_int(field.constant):
            return "integer"

