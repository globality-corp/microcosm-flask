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

from microcosm_flask.fields import LanguageField


class LanguageSchema(Schema):
    language = LanguageField(required=True)


VALID_LANGUAGES = [
    "en-US",
    "fr-FR",
    "en",
]


def test_dump():
    schema = LanguageSchema(strict=True)

    for case in VALID_LANGUAGES:
        result = schema.dump(dict(
            language=case,
        ))
        assert_that(
            result.data["language"],
            is_(equal_to(case)),
        )


def test_load():
    schema = LanguageSchema(strict=True)

    for case in VALID_LANGUAGES:
        result = schema.load(dict(
            language=case,
        ))
        assert_that(
            result.data["language"],
            is_(equal_to(case)),
        )


def test_dump_invalid():
    schema = LanguageSchema(strict=True)
    assert_that(
        calling(schema.dump).with_args(dict(
            language="english",
        )),
        raises(ValidationError),
    )


def test_load_invalid():
    schema = LanguageSchema(strict=True)
    assert_that(
        calling(schema.load).with_args(dict(
            language="english",
        )),
        raises(ValidationError),
    )
