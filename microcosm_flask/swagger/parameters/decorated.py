from typing import Optional

from marshmallow.fields import Field

from microcosm_flask.swagger.parameters.base import ParameterBuilder


SWAGGER_TYPE = "__swagger_type__"
SWAGGER_FORMAT = "__swagger_format__"


class DecoratedParameterBuilder(ParameterBuilder):
    """
    Build parameter from custom attributes (injected by a decorator).

    """
    def supports_field(self, field: Field) -> bool:
        return hasattr(field, SWAGGER_TYPE)

    def parse_format(self, field: Field) -> Optional[str]:
        return getattr(field, SWAGGER_FORMAT, None)

    def parse_type(self, field: Field) -> Optional[str]:
        field_type = getattr(field, SWAGGER_TYPE)
        if isinstance(field_type, list):
            # Ideally we'd use oneOf here, but OpenAPI 2.0 uses the 0.4-draft jsonschema
            # which doesn't include oneOf.
            return None
        return field_type
