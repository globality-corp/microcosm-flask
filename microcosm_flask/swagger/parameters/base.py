from abc import ABC
from collections.abc import (
    Callable,
    Iterable,
    Mapping,
    Sequence,
)
from typing import Any

from marshmallow import Schema
from marshmallow.fields import Field


ENTRY_POINT = "microcosm_flask.swagger.parameters"


class ParameterBuilder(ABC):
    """
    Plugin-aware swagger parameter builder.

    Discovers builder subclasses via the `microcosm_flask.swagger.parameters` entry point
    and delegates to the first compatible implementation.

    """

    def __init__(
        self, build_parameter: Callable[[Schema], Mapping[str, Any]], **kwargs
    ):
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

    def iter_parsed_values(self, field: Field) -> Iterable[tuple[str, Any]]:
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
        return field.dump_default

    def parse_description(self, field: Field) -> str | None:
        """
        Parse the description for the field, if any.

        """
        metadata = field.metadata.get("metadata", {})
        if metadata:
            return metadata.get("description")
        return field.metadata.get("description")

    def parse_enum_values(self, field: Field) -> Sequence | None:
        """
        Parse enumerated value for enum fields, if any.

        """
        return None

    def parse_format(self, field: Field) -> str | None:
        """
        Parse the format for the field, if any.

        """
        return None

    def parse_items(self, field: Field) -> Mapping[str, Any] | None:
        """
        Parse the child item type for list fields, if any.

        """
        return None

    def parse_ref(self, field: Field) -> str | None:
        """
        Parse the reference type for nested fields, if any.

        """
        return None

    def parse_type(self, field: Field) -> str | None:
        """
        Parse the type for the field, if any.

        """
        return None
