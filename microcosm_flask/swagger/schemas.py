"""
Generate JSON Schema for Marshmallow schemas.

"""
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    Tuple,
)

from marshmallow import Schema
from marshmallow.fields import Field, List, Nested

from microcosm_flask.naming import name_for
from microcosm_flask.swagger.naming import type_name


class Schemas:
    """
    Swagger schema builder.

    """
    def __init__(self, build_parameter: Callable[[Schema], Mapping[str, Any]]):
        self.build_parameter = build_parameter

    def build(self, schema: Schema) -> Mapping[str, Any]:
        """
        Build JSON schema from a marshmallow schema.

        """
        fields = list(self.iter_fields(schema))

        properties = {
            field.name: self.build_parameter(field)
            for name, field in fields
        }

        result = dict(
            type="object",
            properties=properties,
        )

        required_fields = [
            name
            for name, field in fields
            if field.required and not field.allow_none
        ]

        if required_fields:
            result["required"] = required_fields

        return result

    def iter_fields(self, schema: Schema) -> Iterable[Tuple[str, Field]]:
        """
        Iterate through marshmallow schema fields.

        Generates: name, field pairs

        """
        for name in sorted(schema.fields.keys()):
            field = schema.fields[name]
            yield field.dump_to or name, field

    def iter_schemas(self, schema: Schema) -> Iterable[Tuple[str, Any]]:
        """
        Build zero or more JSON schemas for a marshmallow schema.

        Generates: name, schema pairs.

        """
        if not schema:
            return

        yield self.to_tuple(schema)

        for name, field in self.iter_fields(schema):
            if isinstance(field, Nested):
                yield self.to_tuple(field.schema)
                yield from self.iter_schemas(field.schema)

            if isinstance(field, List) and isinstance(field.container, Nested):
                yield self.to_tuple(field.container.schema)
                yield from self.iter_schemas(field.container.schema)

    def to_tuple(self, schema: Schema) -> Tuple[str, Any]:
        return type_name(name_for(schema)), self.build(schema)
