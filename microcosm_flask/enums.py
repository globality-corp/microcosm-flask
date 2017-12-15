from collections import namedtuple
from enum import Enum, unique

from microcosm_flask.formatting import (
    JSONFormatter,
    CSVFormatter,
    JSON_CONTENT_TYPE,
    CSV_CONTENT_TYPE,
)

ResponseFormatSpec = namedtuple("ResponseFormatSpec", ["content_type", "formatter"])


@unique
class ResponseFormats(Enum):
    CSV = ResponseFormatSpec(
        content_type=CSV_CONTENT_TYPE,
        formatter=CSVFormatter,
    )
    JSON = ResponseFormatSpec(
        content_type=JSON_CONTENT_TYPE,
        formatter=JSONFormatter,
    )
