from copy import deepcopy

from inflection import camelize, underscore
from marshmallow import Schema

from microcosm_flask.naming import name_for
from microcosm_flask.swagger.naming import type_name


def _get_fields_and_make_required(schema_cls, selected_fields):
    associated_fields = {}
    for field_name in selected_fields:
        field = deepcopy(schema_cls._declared_fields[field_name])
        field.required = True
        associated_fields[field_name] = field

    return associated_fields


def associated_schemas_attr_name(schema_cls):
    return f"_associated_schemas_{underscore(schema_cls.__name__)}"


def associated_schema_name(schema_cls, name_suffix):
    return f"{type_name(name_for(schema_cls))}{camelize(name_suffix)}Schema"


def add_associated_schema(name_suffix, selected_fields=()):
    """
    Derive a schema as a subset of fields from the schema class being decorated,
    and add that derived schema as an attribute on the decorated schema.
    All fields from the derived schema are marked as required.

    This allows us to expose the derived schema in the swagger definition.

    """
    def decorator(schema_cls):
        associated_fields = _get_fields_and_make_required(schema_cls, selected_fields)

        # Use the class name in the attribute name to avoid sharing with children classes
        attr_name = associated_schemas_attr_name(schema_cls)
        associated_schema = type(
            associated_schema_name(schema_cls, name_suffix),
            (Schema,),
            associated_fields,
        )
        try:
            getattr(schema_cls, attr_name).append(associated_schema)
        except AttributeError:
            setattr(
                schema_cls,
                attr_name,
                [associated_schema],
            )
        return schema_cls

    return decorator
