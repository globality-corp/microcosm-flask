"""
Test cleaned field.

"""
from hamcrest import assert_that, equal_to, is_
from marshmallow import Schema

from microcosm_flask.fields import CleanedField

printable_ascii = "~}|{zyxwvutsrqponmlkjihgfedcba`_^]\\[ZYXWVUTSRQPONMLKJIHGFEDCBA@?>="\
    + "<;:9876543210/.-,+*)(\'&%$#\"! "
control_chars = "\u0000\u0001\u0002\u0003\u0004\u0005\u0006\u0007\u0008\u0009\u000a"\
    + "\u000b\u000c\u000d\u000e\u000f\u0010\u0011\u0012\u0013\u0014\u0015\u0016\u0017"\
    + "\u0018\u0019\u001a\u001b\u001c\u001d\u001e\u001f"
spanish_chars = "áéíóúüñ¿¡ÁÁÉÍÓÚÜÑ"
portuguese_chars = "ãáàâçéêíõóôúüÃÁÀÂÇÉÊÍÕÓÔÚÜ"

comment_text = printable_ascii + control_chars + spanish_chars + portuguese_chars
comment_text_cleaned = printable_ascii + spanish_chars + portuguese_chars


class CleanedStringSchema(Schema):
    str = CleanedField(required=True)


def test_load():
    schema = CleanedStringSchema()

    result = schema.load(dict(
        str=comment_text,
    ))
    assert_that(
        result["str"],
        is_(equal_to(comment_text_cleaned)),
    )
