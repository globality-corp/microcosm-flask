from typing import Sequence

from marshmallow.fields import Field

from microcosm_flask.swagger.parameters.base import ParameterBuilder


def is_int(value):
    try:
        int(value)
    except Exception:
        return False
    else:
        return True


class EnumParameterBuilder(ParameterBuilder):
    """
    Build an enum parameter.

    """
    def supports_field(self, field: Field) -> bool:
        return bool(getattr(field, "enum", None))

    def parse_format(self, field: Field) -> None:
        return None

    def parse_type(self, field: Field) -> str:
        enum_values = self.parse_enum_values(field)

        if all((isinstance(enum_value, str) for enum_value in enum_values)):
            return "string"
        elif all((is_int(enum_value) for enum_value in enum_values)):
            return "integer"
        else:
            raise Exception(f"Cannot infer enum type for field: {field.name}")

    def parse_enum_values(self, field: Field) -> Sequence:
        enum = getattr(field, "enum", None)
        return [
            choice.value if field.by_value else choice.name
            for choice in enum
        ]
