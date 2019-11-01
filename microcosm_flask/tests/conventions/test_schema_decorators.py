from hamcrest import (
    assert_that,
    calling,
    equal_to,
    raises,
)

from microcosm_flask.decorators.schemas import (
    add_associated_schema,
    associated_schema_name,
    get_associated_schema,
)
from microcosm_flask.tests.conventions.fixtures import PersonSchema


class TestDecorators:

    def setup(self):
        pass

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

    def test_raise_on_duplicate_suffix(self):
        """
        Registering an associated schema with an already-used suffix should raise

        """
        decorator = add_associated_schema("Foo", [])
        assert_that(
            calling(decorator).with_args(PersonSchema),
            raises(ValueError),
        )
