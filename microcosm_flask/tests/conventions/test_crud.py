"""
CRUD convention tests.

"""
from enum import Enum

from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    is_,
)
from marshmallow.fields import String
from microcosm.api import create_object_graph

from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.fields import EnumField, QueryStringList
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation
from microcosm_flask.paging import OffsetLimitPageSchema
from microcosm_flask.tests.conventions.fixtures import (
    ADDRESS_ID_1,
    PERSON_ID_1,
    PERSON_ID_2,
    PERSON_ID_3,
    Address,
    AddressSchema,
    DeleteAddressSchema,
    NewPersonBatchSchema,
    NewPersonSchema,
    Person,
    PersonBatchSchema,
    PersonLookupSchema,
    PersonSchema,
    address_delete,
    address_retrieve,
    address_search,
    person_create,
    person_delete,
    person_replace,
    person_retrieve,
    person_search,
    person_update,
    person_update_batch,
)


class TestEnum(Enum):
    A = "A"
    B = "B"

    def __str__(self):
        return self.value


class SearchAddressPageSchema(OffsetLimitPageSchema):
    list_param = QueryStringList(String())
    enum_param = EnumField(TestEnum)


def add_request_id(headers, response_data):
    headers["X-Request-Id"] = "request-id"


PERSON_MAPPINGS = {
    Operation.Create: (person_create, NewPersonSchema(), PersonSchema(), add_request_id),
    Operation.Delete: (person_delete,),
    Operation.UpdateBatch: (person_update_batch, NewPersonBatchSchema(), PersonBatchSchema()),
    Operation.Replace: (person_replace, NewPersonSchema(), PersonSchema()),
    Operation.Retrieve: (person_retrieve, PersonLookupSchema(), PersonSchema()),
    Operation.Search: (person_search, OffsetLimitPageSchema(), PersonSchema()),
    Operation.Update: (person_update, NewPersonSchema(), PersonSchema()),
}


ADDRESS_MAPPINGS = {
    Operation.Delete: (address_delete, DeleteAddressSchema(), AddressSchema()),
    Operation.Retrieve: (address_retrieve, AddressSchema()),
    Operation.Search: (address_search, SearchAddressPageSchema(), AddressSchema()),
}


class TestCRUD:

    def setup(self):
        self.graph = create_object_graph(name="example", testing=True)
        person_ns = Namespace(subject=Person)
        address_ns = Namespace(subject=Address)
        configure_crud(self.graph, person_ns, PERSON_MAPPINGS)
        configure_crud(self.graph, address_ns, ADDRESS_MAPPINGS)
        self.client = self.graph.flask.test_client()

    def assert_response(self, response, status_code, data=None):
        # always validate status code
        assert_that(response.status_code, is_(equal_to(status_code)))

        # expect JSON data except on 204
        if status_code == 204:
            response_data = None
        else:
            response_data = response.json

        # validate data if provided
        if response_data is not None and data is not None:
            assert_that(response_data, is_(equal_to(data)))

    def test_search(self):
        uri = "/api/person"
        response = self.client.get(uri)
        self.assert_response(response, 200, {
            "count": 1,
            "offset": 0,
            "limit": 20,
            "items": [{
                "id": str(PERSON_ID_1),
                "firstName": "Alice",
                "lastName": "Smith",
                "_links": {
                    "self": {
                        "href": "http://localhost/api/person/{}".format(PERSON_ID_1),
                    }
                },
            }],
            "_links": {
                "self": {
                    "href": "http://localhost/api/person?offset=0&limit=20",
                }
            }
        })

    def test_count(self):
        uri = "/api/person"
        response = self.client.head(uri)
        assert_that(response.status_code, is_(equal_to(200)))
        assert_that(response.headers["X-Total-Count"], is_(equal_to(str(1))))

    def test_search_with_context(self):
        uri = "/api/address".format(PERSON_ID_1)
        response = self.client.get(uri)
        self.assert_response(response, 200, {
            "count": 1,
            "offset": 0,
            "limit": 20,
            "items": [{
                "id": str(ADDRESS_ID_1),
                "addressLine": "21 Acme St., San Francisco CA 94110",
                "_links": {
                    "self": {
                        "href": "http://localhost/api/address/{}".format(ADDRESS_ID_1),
                    }
                },
            }],
            "_links": {
                "self": {
                    "href": "http://localhost/api/address?offset=0&limit=20",
                }
            }
        })

    def test_reuse_search_self_link(self):
        uri = "/api/address?list_param=a,b,c&enum_param=A".format(PERSON_ID_1)
        response = self.client.get(uri)
        response_data = response.json
        response = self.client.get(response_data["_links"]["self"]["href"])
        self.assert_response(response, 200, {
            "count": 1,
            "offset": 0,
            "limit": 20,
            "items": [{
                "id": str(ADDRESS_ID_1),
                "addressLine": "a,b,c3A",
                "_links": {
                    "self": {
                        "href": "http://localhost/api/address/{}".format(ADDRESS_ID_1),
                    }
                },
            }],
            "_links": {
                "self": {
                    "href": "http://localhost/api/address?offset=0&limit=20&enum_param=A&list_param=a%2Cb%2Cc",
                }
            }
        })

    def test_delete_with_params(self):
        uri = "/api/address/{}?address_clock=123".format(ADDRESS_ID_1)
        response = self.client.delete(uri)
        self.assert_response(response, 204)

    def test_create(self):
        request_data = {
            "firstName": "Bob",
            "lastName": "Jones",
        }
        response = self.client.post("/api/person", json=request_data)
        self.assert_response(response, 201, {
            "id": str(PERSON_ID_2),
            "firstName": "Bob",
            "lastName": "Jones",
            "_links": {
                "self": {
                    "href": "http://localhost/api/person/{}".format(PERSON_ID_2),
                }
            },
        })
        assert_that(response.headers["X-Person-Id"], is_(equal_to(str(PERSON_ID_2))))
        assert_that(response.headers["X-Request-Id"], is_(equal_to("request-id")))

    def test_create_empty_object(self):
        response = self.client.post("/api/person", data='{}')
        self.assert_response(response, 422)
        response_data = response.json
        assert_that(response_data["context"]["errors"], contains_inanyorder(
            {
                "message": "Could not validate field: lastName",
                "field": "lastName",
                "reasons": [
                    "Missing data for required field.",
                ],
            }, {
                "message": "Could not validate field: firstName",
                "field": "firstName",
                "reasons": [
                    "Missing data for required field.",
                ],
            }
        ))

    def test_create_malformed(self):
        request_data = {
            "lastName": "Jones",
        }
        response = self.client.post("/api/person", json=request_data)
        self.assert_response(response, 422, {
            "code": 422,
            "message": "Validation error",
            "retryable": False,
            "context": {
                "errors": [{
                    "message": "Could not validate field: firstName",
                    "field": "firstName",
                    "reasons": [
                        "Missing data for required field.",
                    ],
                }]
            }
        })

    def test_update_batch(self):
        request_data = {
            "items": [{
                "firstName": "Bob",
                "lastName": "Jones",
            }],
        }
        response = self.client.patch("/api/person", json=request_data)
        self.assert_response(response, 200, {
            "items": [{
                "id": str(PERSON_ID_2),
                "firstName": "Bob",
                "lastName": "Jones",
                "_links": {
                    "self": {
                        "href": "http://localhost/api/person/{}".format(PERSON_ID_2),
                    }
                },
            }],
        })

    def test_retrieve(self):
        uri = "/api/person/{}".format(PERSON_ID_1)
        response = self.client.get(uri)
        self.assert_response(response, 200, {
            "id": str(PERSON_ID_1),
            "firstName": "Alice",
            "lastName": "Smith",
            "_links": {
                "self": {
                    "href": "http://localhost/api/person/{}".format(PERSON_ID_1),
                }
            },
        })

    def test_retrieve_qs(self):
        uri = "/api/person/{}?family_member=true".format(PERSON_ID_1)
        response = self.client.get(uri)
        self.assert_response(response, 200, {
            "id": str(PERSON_ID_3),
            "firstName": "Charlie",
            "lastName": "Smith",
            "_links": {
                "self": {
                    "href": "http://localhost/api/person/{}".format(PERSON_ID_3),
                }
            },
        })

    def test_retrieve_not_found(self):
        uri = "/api/person/{}".format(PERSON_ID_2)
        response = self.client.get(uri)
        self.assert_response(response, 404)

    def test_delete(self):
        uri = "/api/person/{}".format(PERSON_ID_1)
        response = self.client.delete(uri)
        self.assert_response(response, 204)

    def test_delete_not_found(self):
        uri = "/api/person/{}".format(PERSON_ID_2)
        response = self.client.delete(uri)
        self.assert_response(response, 404)

    def test_replace(self):
        uri = "/api/person/{}".format(PERSON_ID_1)
        request_data = {
            "firstName": "Bob",
            "lastName": "Jones",
        }
        response = self.client.put(uri, json=request_data)
        self.assert_response(response, 200, {
            "id": str(PERSON_ID_1),
            "firstName": "Bob",
            "lastName": "Jones",
            "_links": {
                "self": {
                    "href": "http://localhost/api/person/{}".format(PERSON_ID_1),
                }
            },
        })

    def test_update(self):
        uri = "/api/person/{}".format(PERSON_ID_1)
        request_data = {
            "firstName": "Bob",
        }
        response = self.client.patch(uri, json=request_data)
        self.assert_response(response, 200, {
            "id": str(PERSON_ID_1),
            "firstName": "Bob",
            "lastName": "Smith",
            "_links": {
                "self": {
                    "href": "http://localhost/api/person/{}".format(PERSON_ID_1),
                }
            },
        })

    def test_update_not_found(self):
        uri = "/api/person/{}".format(PERSON_ID_2)
        request_data = {
            "firstName": "Bob",
        }
        response = self.client.patch(uri, json=request_data)
        self.assert_response(response, 404)
