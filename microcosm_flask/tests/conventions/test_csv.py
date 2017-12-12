"""
CRUD convention tests.

"""
from csv import reader
from six import StringIO

from enum import Enum

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    has_length,
    is_,
    starts_with,
)

from marshmallow.fields import String

from microcosm.api import create_object_graph
from microcosm_flask.enums import ResponseFormats
from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.conventions.base import EndpointDefinition
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation
from microcosm_flask.paging import OffsetLimitPageSchema
from microcosm_flask.fields import QueryStringList, EnumField
from microcosm_flask.tests.conventions.fixtures import (
    Address,
    AddressCSVSchema,
    address_search,
    person_search,
    Person,
    PersonCSVSchema,
    PERSON_ID_1,
)


class TestEnum(Enum):
    A = "A"
    B = "B"

    def __str__(self):
        return self.value


class SearchAddressPageSchema(OffsetLimitPageSchema):
    list_param = QueryStringList(String())
    enum_param = EnumField(TestEnum)


def add_request_id(headers):
    headers["X-Request-Id"] = "request-id"


PERSON_MAPPINGS = {
    Operation.Search: EndpointDefinition(
        func=person_search,
        request_schema=OffsetLimitPageSchema(),
        response_schema=PersonCSVSchema(),
        response_formats=[ResponseFormats.JSON, ResponseFormats.CSV],
    ),
}


ADDRESS_MAPPINGS = {
    Operation.Search: EndpointDefinition(
        func=address_search,
        request_schema=SearchAddressPageSchema(),
        response_schema=AddressCSVSchema(),
        response_formats=[ResponseFormats.JSON, ResponseFormats.CSV],
    ),
}


class TestCSV(object):

    def setup(self):
        self.graph = create_object_graph(name="example", testing=True)
        person_ns = Namespace(subject=Person)
        address_ns = Namespace(subject=Address)
        configure_crud(self.graph, person_ns, PERSON_MAPPINGS)
        configure_crud(self.graph, address_ns, ADDRESS_MAPPINGS)
        self.client = self.graph.flask.test_client()

    def assert_csv_response(self, response, status_code, expected_lines=None):
        assert_that(response.headers["Content-Type"], starts_with("text/csv"))
        # always validate status code
        assert_that(response.status_code, is_(equal_to(status_code)))

        # expect JSON data except on 204
        if status_code == 204:
            response_lines = None
        else:
            response_lines = [row for row in reader(StringIO(response.data.decode("utf-8")))]

        # validate data if provided
        assert_that(
            response_lines,
            has_length(len(expected_lines)),
        )
        if response_lines is not None and expected_lines is not None:
            for index, line in enumerate(response_lines):
                assert_that(
                    line,
                    contains(*expected_lines[index]),
                )

    def test_search(self):
        uri = "/api/person"
        response = self.client.get(
            uri,
            headers={"Accept": "text/csv"},
        )
        self.assert_csv_response(
            response,
            200,
            expected_lines=[
                ["id", "firstName", "lastName"],
                [str(PERSON_ID_1), "Alice", "Smith"],
            ]
        )
