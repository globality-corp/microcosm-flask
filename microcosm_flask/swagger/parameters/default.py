from collections import namedtuple
from logging import Logger
from typing import Optional

from marshmallow import fields
from marshmallow.fields import Field
from microcosm_logging.decorators import logger

from microcosm_flask.fields import LanguageField, URIField
from microcosm_flask.swagger.parameters.base import ParameterBuilder


FieldInfo = namedtuple("FieldInfo", ["type", "format"])


FIELD_MAPPINGS = {
    LanguageField: FieldInfo("string", "language"),
    URIField: FieldInfo("string", "uri"),
    fields.Boolean: FieldInfo("boolean", None),
    fields.Date: FieldInfo("string", "date"),
    fields.DateTime: FieldInfo("string", "date-time"),
    fields.Decimal: FieldInfo("number", None),
    fields.Dict: FieldInfo("object", None),
    fields.Email: FieldInfo("string", "email"),
    fields.Field: FieldInfo("object", None),
    fields.Float: FieldInfo("number", "float"),
    fields.Integer: FieldInfo("integer", "int32"),
    fields.Method: FieldInfo("object", None),
    fields.Number: FieldInfo("number", None),
    fields.Raw: FieldInfo("object", None),
    fields.String: FieldInfo("string", None),
    fields.Time: FieldInfo("string", None),
    fields.URL: FieldInfo("string", "url"),
    fields.UUID: FieldInfo("string", "uuid"),
}


@logger
class DefaultParameterBuilder(ParameterBuilder):
    """
    Builds parameters using default field mappings.

    """
    logger: Logger

    def supports_field(self, field: Field) -> bool:
        try:
            FIELD_MAPPINGS[type(field)]
        except KeyError:
            self.logger.exception(
                f"No mapped swagger type for marshmallow field: {field}",
            )
            raise
        else:
            return True

    def parse_format(self, field: Field) -> Optional[str]:
        return FIELD_MAPPINGS[type(field)].format

    def parse_type(self, field: Field) -> Optional[str]:
        return FIELD_MAPPINGS[type(field)].type
