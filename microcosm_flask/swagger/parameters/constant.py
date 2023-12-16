from typing import Any

from marshmallow.fields import Constant, Field

from microcosm_flask.swagger.parameters.base import ParameterBuilder
from microcosm_flask.swagger.parameters.enum import is_int


class ConstantParameterBuilder(ParameterBuilder):
    """
    Builder parameters for constant fields.

    """

    def supports_field(self, field: Field) -> bool:
        return isinstance(field, Constant)

    def parse_default(self, field: Field) -> Any:
        """
        Parse the default value for the field, if any.

        """
        return getattr(field, "constant", None)

    def parse_type(self, field: Field) -> str | None:
        constant = getattr(field, "constant", None)
        if isinstance(constant, list):
            return "array"
        elif isinstance(constant, str):
            return "string"
        elif is_int(constant):
            return "integer"
        return None
