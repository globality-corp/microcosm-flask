from marshmallow.fields import Field, Nested

from microcosm_flask.naming import name_for
from microcosm_flask.swagger.naming import type_name
from microcosm_flask.swagger.parameters.base import ParameterBuilder


class NestedParameterBuilder(ParameterBuilder):
    """
    Builder parameters for nested fields.

    """
    def supports_field(self, field: Field) -> bool:
        return isinstance(field, Nested)

    def parse_ref(self, field: Field) -> str:
        """
        Parse the reference type for nested fields, if any.

        """
        ref_name = type_name(name_for(field.schema))  # type:ignore
        return f"#/definitions/{ref_name}"

    def parse_type(self, field: Field) -> None:
        return None
