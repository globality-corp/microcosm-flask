"""
Health check convention tests.

"""
from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm.api import create_object_graph

from microcosm_flask.namespaces import Namespace
from microcosm_flask.conventions.alias import configure_alias
from microcosm_flask.conventions.base import EndpointDefinition
from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.operations import Operation
from microcosm_flask.swagger.definitions import build_path
from microcosm_flask.tests.conventions.fixtures import (
    Person,
)


PERSON = Person(id=1, first_name="First", last_name="Last")


def find_person_by_name(person_name):
    return PERSON


def find_person(person_id):
    return PERSON


PERSON_MAPPINGS = {
    Operation.Alias: EndpointDefinition(
        func=find_person_by_name,
    ),
    Operation.Retrieve: EndpointDefinition(
        func=find_person,
    ),
}


class TestAlias:

    def setup(self):
        self.graph = create_object_graph(name="example", testing=True)

        self.ns = Namespace(subject=Person)
        configure_crud(self.graph, self.ns, PERSON_MAPPINGS)
        configure_alias(self.graph, self.ns, PERSON_MAPPINGS)

        self.client = self.graph.flask.test_client()

    def test_url_for(self):
        with self.graph.app.test_request_context():
            url = self.ns.url_for(Operation.Alias, person_name="foo")
        assert_that(url, is_(equal_to("http://localhost/api/person/foo")))

    def test_swagger_path(self):
        with self.graph.app.test_request_context():
            path = build_path(Operation.Alias, self.ns)
        assert_that(path, is_(equal_to("/api/person/{person_name}")))

    def test_alias(self):
        response = self.client.get("/api/person/foo")
        assert_that(response.status_code, is_(equal_to(302)))
        assert_that(response.headers["Location"], is_(equal_to("http://localhost/api/person/1")))
