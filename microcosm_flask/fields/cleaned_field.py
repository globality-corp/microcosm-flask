"""
CleanedField Marshmallow field

An extension of the marshmallow fields.String that removes unicode control
characters on deserialization
"""

import regex
from marshmallow import fields


class CleanedField(fields.String):
    def _deserialize(self, value, *args, **kwargs):
        if value is not None:
            # remove control characters
            value = regex.sub(r'\p{C}', '', value)
        return super()._deserialize(value, *args, **kwargs)
