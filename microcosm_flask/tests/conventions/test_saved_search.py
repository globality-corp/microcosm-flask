from hamcrest import (
    assert_that,
    contains,
    has_entries,
    equal_to,
    is_,
)

from microcosm.api import create_object_graph
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation
from microcosm_flask.paging import OffsetLimitPageSchema
from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.conventions.saved_search import configure_saved_search
from microcosm_flask.tests.conventions.fixtures import (
    person_retrieve,
    person_search,
    Person,
    PersonLookupSchema,
    PersonSchema,
    PERSON_ID_1,
)


class PersonSearch:
    pass


class TestSavedSearch:

    def setup(self):
        self.graph = create_object_graph(name="example", testing=True)
        self.person_ns = Namespace(subject=Person)
        self.ns = Namespace(subject=PersonSearch)
        # ensure that link hrefs work
        configure_crud(self.graph, self.person_ns, {
            Operation.Retrieve: (person_retrieve, PersonLookupSchema(), PersonSchema()),
        })
        # enable saved search
        configure_saved_search(self.graph, self.ns, {
            Operation.SavedSearch: (person_search, OffsetLimitPageSchema(), PersonSchema()),
        })
        self.client = self.graph.flask.test_client()

    def test_saved_search(self):
        uri = "/api/person_search"
        response = self.client.post(uri)

        assert_that(response.status_code, is_(equal_to(200)))
        assert_that(
            response.json,
            has_entries(
                count=1,
                limit=20,
                offset=0,
                items=contains(
                    has_entries(
                        id=str(PERSON_ID_1),
                        firstName="Alice",
                        lastName="Smith",
                    ),
                ),
            ),
        )
