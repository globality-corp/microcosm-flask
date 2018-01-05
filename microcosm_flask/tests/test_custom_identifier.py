"""
Identifier type may be overridden.

"""
from json import dumps, loads
from hashlib import sha256

from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    is_,
)
from microcosm.api import binding, create_object_graph
from microcosm.loaders import load_from_dict
from werkzeug.routing import BaseConverter

from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.conventions.base import EndpointDefinition
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation
from microcosm_flask.tests.conventions.fixtures import (
    Person,
    PersonSchema,
    PERSON_1,
    PERSON_2,
)


class ContentBasedAddressConverter(BaseConverter):
    """
    Example of a customer identifier type: in this case a content-based address.

    """

    @staticmethod
    def make_hash(obj):
        # naive content normalization function
        content = dumps({
            key: str(value)
            for key, value in obj.__dict__.items()
        }, sort_keys=True)
        return sha256(content.encode("utf-8")).hexdigest()


@binding("cba")
def configure_hash_converter(graph):
    graph.flask.url_map.converters["cba"] = ContentBasedAddressConverter


PEOPLE = [
    PERSON_1,
    PERSON_2,
]


def retrieve_person(person_id):
    return next(
        person
        for person in PEOPLE
        if ContentBasedAddressConverter.make_hash(person) == person_id
    )


PERSON_MAPPINGS = {
    Operation.Retrieve: EndpointDefinition(
        func=retrieve_person,
        response_schema=PersonSchema(),
    ),
}


class TestIdentifierType:

    def setup(self):
        loader = load_from_dict(
            route=dict(
                converters=[
                    "cba"
                ],
            ),
        )
        self.graph = create_object_graph(name="example", testing=True, loader=loader)
        assert_that(self.graph.config.route.converters, contains_inanyorder("uuid", "cba"))
        self.person_ns = Namespace(
            subject=Person,
            # use custom identifier type
            identifier_type="cba",
        )
        configure_crud(self.graph, self.person_ns, PERSON_MAPPINGS)
        self.client = self.graph.flask.test_client()

    def test_content_based_address(self):
        hash_id = ContentBasedAddressConverter.make_hash(PERSON_1)
        response = self.client.get("/api/person/{}".format(hash_id))

        assert_that(response.status_code, is_(equal_to(200)))
        response_data = loads(response.get_data().decode("utf-8"))
        assert_that(response_data["id"], is_(equal_to(str(PERSON_1.id))))
