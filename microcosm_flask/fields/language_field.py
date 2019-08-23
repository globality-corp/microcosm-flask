"""
An RFC-1766 and xsd:language compatible field.

"""
from re import match

from marshmallow.fields import String


# taken from: http://books.xmlschemata.org/relaxng/ch19-77191.html
LANGUAGE_PATTERN = r"^([a-zA-Z]{2}|[iI]-[a-zA-Z]+|[xX]-[a-zA-Z]{1,8})(-[a-zA-Z]{1,8})*$"


class LanguageField(String):
    default_error_messages = dict(
        invalid_language="Not an RFC-1766 language",
    )

    def _validated(self, value):
        if not match(LANGUAGE_PATTERN, value):
            self.fail("invalid_language")
        return value

    def _serialize(self, value, attr, obj, **kwargs):
        validated = str(self._validated(value)) if value is not None else None
        return super(LanguageField, self)._serialize(validated, attr, obj)

    def _deserialize(self, value, attr, data, **kwargs):
        return self._validated(value)
