from collections import namedtuple
from enum import Enum, unique

from microcosm_flask.formatting import (
    JSONFormatter,
    CSVFormatter,
    JSON_CONTENT_TYPE,
    CSV_CONTENT_TYPE,
)

ResponseFormatSpec = namedtuple("ResponseFormatSpec", ["content_type", "formatter", "priority"])


@unique
class ResponseFormats(Enum):
    CSV = ResponseFormatSpec(
        content_type=CSV_CONTENT_TYPE,
        formatter=CSVFormatter,
        priority=100,
    )
    JSON = ResponseFormatSpec(
        content_type=JSON_CONTENT_TYPE,
        formatter=JSONFormatter,
        priority=1,
    )

    @property
    def content_type(self):
        return self.value.content_type

    @property
    def priority(self):
        return self.value.priority

    def matches(self, content_type):
        this = self.content_type.split("/", 1)
        that = content_type.split("/", 1)

        for (this_part, that_part) in zip(this, that):
            if that_part != "*" and this_part != that_part:
                return False

        return True

    @classmethod
    def prioritized(cls):
        return sorted(cls, key=lambda this: this.priority)
