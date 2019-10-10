from typing import Any, Mapping

from marshmallow.fields import Field, List

from microcosm_flask.swagger.parameters.base import ParameterBuilder


class ListParameterBuilder(ParameterBuilder):
    """
    Builder parameters for nested fields.

    """
    def supports_field(self, field: Field) -> bool:
        return isinstance(field, List)

    def parse_items(self, field: Field) -> Mapping[str, Any]:
        """
        Parse the child item type for list fields, if any.

        """
        return self.build_parameter(field.inner)  # type: ignore

    def parse_type(self, field: Field) -> str:
        return "array"
