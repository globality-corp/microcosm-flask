"""
Generate JSON Schema for Marshmallow schemas.

"""
from logging import getLogger
from six import string_types

from marshmallow import fields

from microcosm_flask.fields import (
    EnumField,
    LanguageField,
    QueryStringList,
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
    except:
        return False
    else:
        return True


def swagger_field(field, swagger_type="string", swagger_format=None):
    setattr(field, SWAGGER_TYPE, swagger_type)
    setattr(field, SWAGGER_FORMAT, swagger_format)
    return field


def build_parameter(field):
    """
    Build a parameter from a marshmallow field.

    See: https://github.com/marshmallow-code/apispec/blob/dev/apispec/ext/marshmallow/swagger.py#L81

    """
    try:
        field_type, field_format = FIELD_MAPPINGS[type(field)]
    except KeyError:
        if hasattr(field, SWAGGER_TYPE):
            field_type = getattr(field, SWAGGER_TYPE)
            field_format = getattr(field, SWAGGER_FORMAT, None)
        else:
            logger.exception("No mapped swagger type for marshmallow field: {}".format(
                field,
            ))
            raise

    parameter = {}
    if field_type:
        parameter["type"] = field_type
    if field.metadata.get("description"):
        parameter["description"] = field.metadata["description"]
    if field_format:
        parameter["format"] = field_format
    if field.default:
        parameter["default"] = field.default
    # NB: all marshallow Number fields support as_string
    if getattr(field, 'as_string', None):
        parameter["type"] = "string"
        if isinstance(field, fields.Decimal):
            parameter["format"] = "decimal"

    # enums
    enum = getattr(field, "enum", None)
    if enum:
        enum_values = [
            choice.value if field.by_value else choice.name
            for choice in enum
        ]
        if all((isinstance(enum_value, string_types) for enum_value in enum_values)):
            enum_type = "string"
        elif all((is_int(enum_value) for enum_value in enum_values)):
            enum_type = "integer"
        else:
            raise Exception("Cannot infer enum type for field: {}".format(field.name))

        parameter["type"] = enum_type
        parameter["enum"] = enum_values

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
