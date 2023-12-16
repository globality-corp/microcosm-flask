from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_key,
    has_length,
    raises,
)
from marshmallow import Schema, fields

from microcosm_flask.decorators.schemas import (
    add_associated_schema,
    associated_schema_name,
    get_associated_schema,
    get_fields_from_schema,
    set_associated_schema,
)
from microcosm_flask.tests.conventions.fixtures import PersonSchema


class TestDecorators:
    def setup_method(self):
        pass

    def test_get_fields_from_schema(self):
        class SomeSchema(Schema):
            someField = fields.String(attribute="some_field")
            anotherField = fields.Integer(attribute="another_field")

        selected_fields = get_fields_from_schema(SomeSchema, ["someField"])
        assert_that(selected_fields, has_length(1))
        assert_that(selected_fields, has_key("someField"))

    def test_get_associated_schema(self):
        """
        Associated schemas can be retrieved by suffix

        """
        associated_schema = get_associated_schema(PersonSchema, "Foo")
        assert_that(
            associated_schema.__name__,
            equal_to("PersonFooSchema"),
        )

        assert_that(
            calling(get_associated_schema).with_args(PersonSchema, "Bar"),
            raises(KeyError),
        )

    def test_associated_schema_name(self):
        """
        Associated schema name has the suffix insert before `-Schema`

        """
        assert_that(
            associated_schema_name(PersonSchema, "Suffix"),
            equal_to("PersonSuffixSchema"),
        )

    def test_override_inheritance(self):
        """
        Registering an associated schema with an already-used suffix should raise

        """

        class ParentSchema(Schema):
            someField = fields.String(attribute="some_field")

        add_associated_schema("Bar", [], (ParentSchema,))(PersonSchema)
        associated_schema = get_associated_schema(PersonSchema, "Bar")

        assert_that(
            associated_schema._declared_fields,
            has_key("someField"),
        )

    def test_raise_on_duplicate_suffix(self):
        """
        Registering an associated schema with an already-used suffix should raise

        """
        decorator = add_associated_schema("Foo", [])
        assert_that(
            calling(decorator).with_args(PersonSchema),
            raises(ValueError),
        )

    def test_set_associated_schema(self):
        class SomeSchema(Schema):
            someField = fields.String(attribute="some_field")

        class AnotherSchema(Schema):
            anotherField = fields.Integer(attribute="another_field")

        set_associated_schema(SomeSchema, "Suffix", AnotherSchema)

        assert_that(
            get_associated_schema(SomeSchema, "Suffix")._declared_fields,
            has_key("anotherField"),
        )
