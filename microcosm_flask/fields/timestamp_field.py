"""
A timestaamp-valued field.

Supports both UNIX epoch (preferred) and ISO 8601 (discouraged) encodings.

"""
from datetime import datetime

from dateutil import parser
from marshmallow.fields import Field, ValidationError


class TimestampField(Field):
    """
    Timestamp valued field, as either a unix timestamp (default) or isoformat string.

    """
    EPOCH = datetime(1970, 1, 1)

    def __init__(self, use_isoformat=False, *args, **kwargs):
        self.use_isoformat = use_isoformat
        super(TimestampField, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        """
        Serialize value as a timestamp, either as a Unix timestamp (in float second) or a UTC isoformat string.

        """
        if value is None:
            return None

        if self.use_isoformat:
            return datetime.utcfromtimestamp(value).isoformat()
        else:
            return value

    def _deserialize(self, value, attr, obj, **kwargs):
        """
        Deserialize value as a Unix timestamp (in float seconds).

        Handle both numeric and UTC isoformat strings.

        """
        if value is None:
            return None

        try:
            return float(value)
        except ValueError:
            parsed = parser.parse(value)
            if parsed.tzinfo:
                if parsed.utcoffset().total_seconds():
                    raise ValidationError("Timestamps must be defined in UTC")
                parsed = parsed.replace(tzinfo=None)
            return (parsed - TimestampField.EPOCH).total_seconds()
