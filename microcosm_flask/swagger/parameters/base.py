from abc import ABC
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

from marshmallow import Schema
from marshmallow.fields import Field


ENTRY_POINT = "microcosm_flask.swagger.parameters"


class ParameterBuilder(ABC):
    """
    Plugin-aware swagger parameter builder.

    Discovers builder subclasses via the `microcosm_flask.swagger.parameters` entry point
    and delegates to the first compatible implementation.

    """
    def __init__(self, build_parameter: Callable[[Schema], Mapping[str, Any]]):
        self.build_parameter = build_parameter
        self.parsers = {
            "default": self.parse_default,
            "description": self.parse_description,
            "enum": self.parse_enum_values,
            "format": self.parse_format,
            "$ref": self.parse_ref,
            "type": self.parse_type,
            "items": self.parse_items,
        }

    def build(self, field: Field) -> Mapping[str, Any]:
        """
        Build a parameter.

        """
        return dict(self.iter_parsed_values(field))

    def supports_field(self, field: Field) -> bool:
        """
        Does this builder support this kind of field?

        """
        return False

    def iter_parsed_values(self, field: Field) -> Iterable[Tuple[str, Any]]:
        """
        Walk the dictionary of parsers and emit all non-null values.

        """
        for key, func in self.parsers.items():
            value = func(field)
            if not value:
                continue
            yield key, value

    def parse_default(self, field: Field) -> Any:
        """
        Parse the default value for the field, if any.

        """
        return field.default

    def parse_description(self, field: Field) -> Optional[str]:
        """
        Parse the description for the field, if any.

        """
        return field.metadata.get("description")

    def parse_enum_values(self, field: Field) -> Optional[Sequence]:
        """
        Parse enumerated value for enum fields, if any.

        """
        return None

    def parse_format(self, field: Field) -> Optional[str]:
        """
        Parse the format for the field, if any.

        """
        return None

    def parse_items(self, field: Field) -> Optional[Mapping[str, Any]]:
        """
        Parse the child item type for list fields, if any.

        """
        return None

    def parse_ref(self, field: Field) -> Optional[str]:
        """
        Parse the reference type for nested fields, if any.

        """
        return None

    def parse_type(self, field: Field) -> Optional[str]:
        """
        Parse the type for the field, if any.

        """
        return None
