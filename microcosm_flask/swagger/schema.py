"""
Generate JSON Schema for Marshmallow schemas.

"""
from logging import getLogger

from marshmallow import fields

from microcosm_flask.fields import (
    EnumField,
    LanguageField,
    QueryStringList,
    TimestampField,
    URIField,
)
from microcosm_flask.naming import name_for
from microcosm_flask.swagger.naming import type_name


logger = getLogger("microcosm_flask.swagger")


# see: https://github.com/marshmallow-code/apispec/blob/dev/apispec/ext/marshmallow/swagger.py
FIELD_MAPPINGS = {
    EnumField: (None, None),
    LanguageField: ("string", "language"),
    QueryStringList: ("array", None),
    URIField: ("string", "uri"),
    fields.Boolean: ("boolean", None),
    fields.Date: ("string", "date"),
    fields.DateTime: ("string", "date-time"),
    fields.Decimal: ("number", None),
    fields.Dict: ("object", None),
    fields.Email: ("string", "email"),
    fields.Field: ("object", None),
    fields.Float: ("number", "float"),
    fields.Integer: ("integer", "int32"),
    fields.List: ("array", None),
    fields.Method: ("object", None),
    fields.Nested: (None, None),
    fields.Number: ("number", None),
    fields.Raw: ("object", None),
    fields.String: ("string", None),
    fields.Time: ("string", None),
    fields.URL: ("string", "url"),
    fields.UUID: ("string", "uuid"),
}


SWAGGER_TYPE = "__swagger_type__"
SWAGGER_FORMAT = "__swagger_format__"


def is_int(value):
    try:
        int(value)
    except Exception:
        return False
    else:
        return True


def swagger_field(field, swagger_type="string", swagger_format=None):
    """
    Decorator for an existing field type to coerce a specific swagger type/format.

    Usage:

        class MySchema(Schema):
             myfield = swagger_field(fields.Foo(), swagger_type="string")

    """
    setattr(field, SWAGGER_TYPE, swagger_type)
    setattr(field, SWAGGER_FORMAT, swagger_format)
    return field


def resolve_tagged_field(field):
    """
    Fields tagged with `swagger_field` shoudl respect user definitions.

    """
    field_type = getattr(field, SWAGGER_TYPE)
    field_format = getattr(field, SWAGGER_FORMAT, None)
    if field_format:
        return dict(
            type=field_type,
            format=field_format,
        )
    else:
        return dict(
            type=field_type,
        )


def resolve_enum_field(field):
    """
    Enum fields should include choices.

    """
    enum = getattr(field, "enum", None)
    enum_values = [
        choice.value if field.by_value else choice.name
        for choice in enum
    ]
    if all((isinstance(enum_value, str) for enum_value in enum_values)):
        return dict(
            type="string",
            enum=enum_values,
        )
    elif all((is_int(enum_value) for enum_value in enum_values)):
        return dict(
            type="integer",
            enum=enum_values,
        )
    else:
        raise Exception("Cannot infer enum type for field: {}".format(field.name))


def resolve_timestamp_field(field):
    """
    Timestamp fields should respect configuration.

    """
    if field.use_isoformat:
        return dict(
            type="string",
            format="date-time",
        )
    else:
        return dict(
            type="float",
            format="timestamp",
        )


def resolve_numeric_string_field(field):
    """
    Numeric fields should respect the `as_string` parameter.

    """
    if isinstance(field, fields.Decimal):
        return dict(
            type="string",
            format="decimal",
        )
    else:
        return dict(
            type="string",
        )


def resolve_default_for_field(field):
    """
    Field defaults should be the fallback.

    """
    try:
        field_type, field_format = FIELD_MAPPINGS[type(field)]
        if field_format:
            return dict(
                type=field_type,
                format=field_format,
            )
        elif field_type:
            return dict(
                type=field_type,
            )
        else:
            return dict()
    except KeyError:
        logger.exception("No mapped swagger type for marshmallow field: {}".format(
            field,
        ))
        raise


def build_parameter(field):
    """
    Build a parameter from a marshmallow field.

    See: https://github.com/marshmallow-code/apispec/blob/dev/apispec/ext/marshmallow/swagger.py#L81

    """
    if hasattr(field, SWAGGER_TYPE):
        parameter = resolve_tagged_field(field)
    elif getattr(field, "enum", None):
        parameter = resolve_enum_field(field)
    elif getattr(field, 'as_string', None):
        parameter = resolve_numeric_string_field(field)
    elif isinstance(field, TimestampField):
        parameter = resolve_timestamp_field(field)
    else:
        parameter = resolve_default_for_field(field)

    if field.metadata.get("description"):
        parameter["description"] = field.metadata["description"]

    if field.default:
        parameter["default"] = field.default

    # nested
    if isinstance(field, fields.Nested):
        parameter["$ref"] = "#/definitions/{}".format(type_name(name_for(field.schema)))

    # arrays
    if isinstance(field, fields.List):
        parameter["items"] = build_parameter(field.container)

    return parameter


def build_schema(marshmallow_schema):
    """
    Build JSON schema from a marshmallow schema.

    """
    fields = list(iter_fields(marshmallow_schema))
    required_fields = [
        field.dump_to or name
        for name, field in fields
        if field.required and not field.allow_none
    ]
    schema = {
        "type": "object",
        "properties": {
            field.dump_to or name: build_parameter(field)
            for name, field in fields
        }
    }
    if required_fields:
        schema["required"] = required_fields
    return schema


def iter_fields(marshmallow_schema):
    """
    Iterate through marshmallow schema fields.

    Generates: name, field pairs

    """
    for name in sorted(marshmallow_schema.fields.keys()):
        yield name, marshmallow_schema.fields[name]


def iter_schemas(marshmallow_schema):
    """
    Build zero or more JSON schemas for a marshmallow schema.

    Generates: name, schema pairs.

    """
    if not marshmallow_schema:
        return

    base_schema = build_schema(marshmallow_schema)
    base_schema_name = type_name(name_for(marshmallow_schema))
    yield base_schema_name, base_schema

    for name, field in iter_fields(marshmallow_schema):
        if isinstance(field, fields.Nested):
            nested_schema = build_schema(field.schema)
            nested_schema_name = type_name(name_for(field.schema))
            yield nested_schema_name, nested_schema
            for subname, subfield in iter_schemas(field.schema):
                yield subname, subfield
        if isinstance(field, fields.List) and isinstance(field.container, fields.Nested):
            nested_schema = build_schema(field.container.schema)
            nested_schema_name = type_name(name_for(field.container.schema))
            yield nested_schema_name, nested_schema
            for subname, subfield in iter_schemas(field.container.schema):
                yield subname, subfield
