"""
API interfaces for swagger operations.

"""
from typing import (
    Any,
    Iterable,
    Mapping,
    Tuple,
)

from marshmallow import Schema
from marshmallow.fields import Field

from microcosm_flask.swagger.parameters import Parameters
from microcosm_flask.swagger.schemas import Schemas


def build_schema(schema: Schema) -> Mapping[str, Any]:
    """
    Build JSON schema from a marshmallow schema.

    """
    builder = Schemas(build_parameter=build_parameter)
    return builder.build(schema)


def iter_schemas(schema: Schema) -> Iterable[Tuple[str, Any]]:
    """
    Build zero or more JSON schemas for a marshmallow schema.

    Generates: name, schema pairs.

    """
    builder = Schemas(build_parameter=build_parameter)
    return builder.iter_schemas(schema)


def build_parameter(field: Field) -> Mapping[str, Any]:
    """
    Build JSON parameter from a marshmallow field.

    """
    builder = Parameters()
    return builder.build(field)
