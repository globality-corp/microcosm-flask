from copy import deepcopy
from dataclasses import dataclass
from typing import List, Optional

from inflection import camelize, underscore
from marshmallow import Schema

from microcosm_flask.naming import name_for
from microcosm_flask.swagger.naming import type_name


@dataclass
class SelectedField:
    name: str
    required: Optional[bool] = None


def get_fields_from_schema(schema_cls: Schema, selected_fields: List[SelectedField]):
    """
    Select fields definitions from a schema

    By default, the selected fields will keep the same value for `required` as the source,
    but this can be overriden by passing the right value for `required` to the `SelectedField` instance
    passed in to this method.

    """
    associated_fields = {}
    for selected_field in selected_fields:
        if isinstance(selected_field, str):
            selected_field = SelectedField(selected_field)
        schema_field = deepcopy(schema_cls._declared_fields[selected_field.name])
        if selected_field.required is not None:
            schema_field.required = selected_field.required
        associated_fields[selected_field.name] = schema_field

    return associated_fields


def associated_schemas_attr_name(schema_cls):
    return f"_associated_schemas_{underscore(schema_cls.__name__)}"


def associated_schema_name(schema_cls, name_suffix):
    return f"{type_name(name_for(schema_cls))}{camelize(name_suffix)}Schema"


def get_associated_schema(schema_cls, name_suffix):
    associated_schemas = getattr(schema_cls, associated_schemas_attr_name(schema_cls), {})
    if name_suffix in associated_schemas:
        return associated_schemas[name_suffix]
    raise KeyError(f"Schema {schema_cls} does not have an associated schema with suffix {name_suffix}")


def set_associated_schema(target_cls, name_suffix, associated_schema):
    """
    Add a derived schema as an attribute to a schema class, using conventions
    that will result in the associated schema being exposed in the OpenAPI definition of the service.

    """
    # Use the class name in the attribute name to avoid sharing with children classes
    attr_name = associated_schemas_attr_name(target_cls)
    try:
        associated_schemas = getattr(target_cls, attr_name)
        if name_suffix in associated_schemas:
            raise ValueError(f"Schema {target_cls} already has an associated schema for suffix {name_suffix}")
        associated_schemas[name_suffix] = associated_schema
    except AttributeError:
        setattr(
            target_cls,
            attr_name,
            {name_suffix: associated_schema},
        )


def build_associated_schema(schema_cls, name_suffix, inherits_from, associated_fields):
    """
    Build a schema class, whose name is based on an existing schema.

    """
    return type(
        associated_schema_name(schema_cls, name_suffix),
        inherits_from,
        associated_fields,
    )


def add_associated_schema(name_suffix, selected_fields=(), inherits_from=(Schema,)):
    """
    Derive a schema as a subset of fields from the schema class being decorated,
    and add that derived schema as an attribute on the decorated schema.

    This allows us to expose the derived schema in the swagger definition.

    :name_suffix: Suffix that will added to the decorator schema's definition name to give the
                  name of the exposed definition
    :selected_fields: List of `SelectedField` instances. As a shorthand a list of strings can also
                      be passed, which will make all sected field required

    """
    def decorator(schema_cls):
        associated_fields = get_fields_from_schema(schema_cls, selected_fields)

        associated_schema = build_associated_schema(
            schema_cls,
            name_suffix,
            inherits_from,
            associated_fields,
        )

        set_associated_schema(schema_cls, name_suffix, associated_schema)
        return schema_cls

    return decorator
