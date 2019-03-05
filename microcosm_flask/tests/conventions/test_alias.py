"""
Health check convention tests.

"""
from json import loads

from hamcrest import assert_that, equal_to, has_key, is_
from marshmallow import Schema, fields
from microcosm.api import create_object_graph

from microcosm_flask.conventions.alias import configure_alias
from microcosm_flask.conventions.base import EndpointDefinition
from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.conventions.swagger import configure_swagger
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation
from microcosm_flask.swagger.definitions import build_path
from microcosm_flask.tests.conventions.fixtures import Person


class PersonSchema(Schema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()


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
        response_schema=PersonSchema(),
    ),
}


class TestAlias:

    def setup(self):
        self.graph = create_object_graph(name="example", testing=True)

        self.ns = Namespace(
            subject=Person,
        )
        configure_crud(self.graph, self.ns, PERSON_MAPPINGS)
        configure_alias(self.graph, self.ns, PERSON_MAPPINGS)
        self.graph.config.swagger_convention.operations.append("alias")
        configure_swagger(self.graph)

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

    def test_swagger(self):
        response = self.client.get("/api/swagger")
        assert_that(response.status_code, is_(equal_to(200)))
        data = loads(response.data)

        alias = data["paths"]["/person/{person_name}"]["get"]
        assert_that(
            alias["responses"],
            has_key("302"),
        )

        retrieve = data["paths"]["/person/{person_id}"]["get"]
        assert_that(
            retrieve["responses"],
            has_key("200"),
        )
