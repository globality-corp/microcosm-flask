"""
Test language field.

"""
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    is_,
    raises,
)
from marshmallow import Schema, ValidationError

from microcosm_flask.fields import AsciiEncodedString



class AsciiStringSchema(Schema):
    str = AsciiEncodedString(required=True)


comment_text_unicode = "A nice \u0420\u043e\u0441\u0441\u0438\u044fcomment"
comment_text_cleaned = "A nice comment"


def test_load():
    schema = AsciiStringSchema()

    result = schema.load(dict(
        str=comment_text_unicode,
    ))
    assert_that(
        result["str"],
        is_(equal_to(comment_text_cleaned)),
    )
