from collections import namedtuple
from enum import Enum, unique

from microcosm_flask.formatting import (
    CSVFormatter,
    JSONFormatter,
    HTMLFormatter,
    TextFormatter,
)

ResponseFormatSpec = namedtuple("ResponseFormatSpec", ["content_type", "formatter", "priority"])


@unique
class ResponseFormats(Enum):
    CSV = ResponseFormatSpec(
        content_type=CSVFormatter.CONTENT_TYPE,
        formatter=CSVFormatter,
        priority=100,
    )
    JSON = ResponseFormatSpec(
        content_type=JSONFormatter.CONTENT_TYPE,
        formatter=JSONFormatter,
        priority=1,
    )
    HTML = ResponseFormatSpec(
        content_type=HTMLFormatter.CONTENT_TYPE,
        formatter=HTMLFormatter,
        priority=10,
    )
    TEXT = ResponseFormatSpec(
        content_type=TextFormatter.CONTENT_TYPE,
        formatter=TextFormatter,
        priority=150,
    )

    @property
    def content_type(self):
        return self.value.content_type

    @property
    def priority(self):
        return self.value.priority

    def matches(self, content_types):
        for content_type in content_types.split(","):
            if self.matches_content_type(content_type):
                return True
        return False

    def matches_content_type(self, content_type):
        this = self.content_type.split("/", 1)
        that = content_type.split(";", 1)[0].split("/", 1)

        for (this_part, that_part) in zip(this, that):
            if that_part != "*" and this_part != that_part:
                return False

        return True

    @classmethod
    def prioritized(cls):
        return sorted(cls, key=lambda this: this.priority)
