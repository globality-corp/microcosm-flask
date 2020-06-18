"""
Generate JSON Schema for Marshmallow schemas.

"""
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    Set,
    Tuple,
    Type,
)

from marshmallow import Schema
from marshmallow.fields import Field, List, Nested

from microcosm_flask.decorators.schemas import associated_schemas_attr_name
from microcosm_flask.naming import name_for
from microcosm_flask.swagger.naming import type_name


def definition_name_for_schema(schema_cls):
    return type_name(name_for(schema_cls))


class Schemas:
    """
    Swagger schema builder.

    """
    def __init__(
        self,
        build_parameter: Callable[..., Mapping[str, Any]],
        strict_enums: bool = True,
    ):
        self.build_parameter = build_parameter
        self.strict_enums = strict_enums

        # NB: This will break if this class is ever instantiated and then has
        # `build` called more than once
        self.seen_schemas: Set[Type[Schema]] = set()

    def build(self, schema: Schema) -> Mapping[str, Any]:
        """
        Build JSON schema from a marshmallow schema.

        """
        fields = list(self.iter_fields(schema))

        properties = {
            name: self.build_parameter(field, strict_enums=self.strict_enums)
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
            field_name = field.data_key or name

            yield field_name, field

    def iter_schemas(self, schema: Schema) -> Iterable[Tuple[str, Any]]:
        """
        Build zero or more JSON schemas for a marshmallow schema.

        Generates: name, schema pairs.

        """
        if not schema:
            return

        if type(schema) in self.seen_schemas:
            return

        self.seen_schemas.add(type(schema))

        yield self.to_tuple(schema)

        for associated_schema in getattr(schema, associated_schemas_attr_name(schema.__class__), {}).values():
            yield self.to_tuple(associated_schema())

        for name, field in self.iter_fields(schema):
            if isinstance(field, Nested):
                yield from self.iter_schemas(field.schema)

            if isinstance(field, List) and isinstance(field.inner, Nested):
                yield from self.iter_schemas(field.inner.schema)

    def to_tuple(self, schema: Schema) -> Tuple[str, Any]:
        return definition_name_for_schema(schema), self.build(schema)
