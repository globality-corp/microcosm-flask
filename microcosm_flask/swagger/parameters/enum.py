from typing import (
    Any,
    Callable,
    Mapping,
    Optional,
    Sequence,
)

from marshmallow import Schema
from marshmallow.fields import Field

from microcosm_flask.fields import EnumField
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

    If `strict_enums` is True, the parameter is built using the "enum" format,
    with the allowed values under the "enum" key. Otherwise the parameter is simply considered
    as a string.

    """
    def __init__(
        self,
        build_parameter: Callable[[Schema], Mapping[str, Any]],
        strict_enums: bool = True,
        **kwargs,
    ):
        super().__init__(build_parameter)
        self.strict_enums = strict_enums

    def supports_field(self, field: Field) -> bool:
        return bool(getattr(field, "enum", None))

    def parse_format(self, field: Field) -> Optional[str]:
        if self.is_strict(field):
            return "enum"

        return None

    def parse_type(self, field: Field) -> str:
        enum_values = self._parse_enum_values(field)

        if all((isinstance(enum_value, str) for enum_value in enum_values)):
            return "string"
        elif all((is_int(enum_value) for enum_value in enum_values)):
            return "integer"
        else:
            raise Exception(f"Cannot infer enum type for field: {field.name}")

    def _parse_enum_values(self, field: Field) -> Sequence:
        if not isinstance(field, EnumField):
            raise Exception(f"Cannot parse enum values for non-enum fields: {field.name}")
        return [
            choice.value if field.by_value else choice.name
            for choice in field.enum
        ]

    def parse_enum_values(self, field: Field) -> Optional[Sequence]:
        if self.is_strict(field):
            return self._parse_enum_values(field)

        return None

    def is_strict(self, field: Field) -> bool:
        return (
            isinstance(field, EnumField) and
            self.strict_enums and
            getattr(field.enum, "__openapi_strict__", True)
        )
