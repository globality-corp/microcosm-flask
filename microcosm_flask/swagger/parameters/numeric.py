from typing import Optional

from marshmallow.fields import Decimal, Field

from microcosm_flask.swagger.parameters.base import ParameterBuilder


class NumericParameterBuilder(ParameterBuilder):
    """
    Build a string-formatted numeric parameter.

    """
    def supports_field(self, field: Field) -> bool:
        return bool(getattr(field, "as_string", None))

    def parse_format(self, field: Field) -> Optional[str]:
        if isinstance(field, Decimal):
            return "decimal"
        return None

    def parse_type(self, field: Field) -> str:
        return "string"
