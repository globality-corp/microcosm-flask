"""
CRUD convention tests.

"""
from json import dumps, loads

from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    is_,
)

from microcosm.api import create_object_graph
from microcosm_flask.conventions.crud import configure_crud
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation
from microcosm_flask.paging import PageSchema
from microcosm_flask.tests.conventions.fixtures import (
    Address,
    AddressSchema,
    NewPersonBatchSchema,
    NewPersonSchema,
    address_retrieve,
    address_search,
    person_create,
    person_delete,
    person_replace,
    person_retrieve,
    person_search,
    person_update,
    person_update_batch,
    Person,
    PersonBatchSchema,
    PersonLookupSchema,
    PersonSchema,
    ADDRESS_ID_1,
    PERSON_ID_1,
    PERSON_ID_2,
    PERSON_ID_3,
)


PERSON_MAPPINGS = {
    Operation.Create: (person_create, NewPersonSchema(), PersonSchema()),
    Operation.Delete: (person_delete,),
    Operation.UpdateBatch: (person_update_batch, NewPersonBatchSchema(), PersonBatchSchema()),
    Operation.Replace: (person_replace, NewPersonSchema(), PersonSchema()),
    Operation.Retrieve: (person_retrieve, PersonLookupSchema(), PersonSchema()),
    Operation.Search: (person_search, PageSchema(), PersonSchema()),
    Operation.Update: (person_update, NewPersonSchema(), PersonSchema()),
}


ADDRESS_MAPPINGS = {
    Operation.Retrieve: (address_retrieve, AddressSchema()),
    Operation.Search: (address_search, PageSchema(), AddressSchema()),
}


class TestCrud(object):

    def setup(self):
        self.graph = create_object_graph(name="example", testing=True)
        person_ns = Namespace(subject=Person)
        address_ns = Namespace(subject=Address, path=person_ns.instance_path)
        configure_crud(self.graph, Person, PERSON_MAPPINGS)
        configure_crud(self.graph, address_ns, ADDRESS_MAPPINGS)
        self.client = self.graph.flask.test_client()

    def assert_response(self, response, status_code, data=None):
        # always validate status code
        assert_that(response.status_code, is_(equal_to(status_code)))

        # expect JSON data except on 204
        if status_code == 204:
            response_data = None
        else:
            response_data = loads(response.get_data().decode("utf-8"))

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
        uri = "/api/person/{}/address".format(PERSON_ID_1)
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
                        "href": "http://localhost/api/person/{}/address/{}".format(PERSON_ID_1, ADDRESS_ID_1),
                    }
                },
            }],
            "_links": {
                "self": {
                    "href": "http://localhost/api/person/{}/address?offset=0&limit=20".format(PERSON_ID_1),
                }
            }
        })

    def test_create(self):
        request_data = {
            "firstName": "Bob",
            "lastName": "Jones",
        }
        response = self.client.post("/api/person", data=dumps(request_data))
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

    def test_create_empty_object(self):
        response = self.client.post("/api/person", data='{}')
        self.assert_response(response, 422)
        response_data = loads(response.get_data().decode("utf-8"))
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
        response = self.client.post("/api/person", data=dumps(request_data))
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
        response = self.client.patch("/api/person", data=dumps(request_data))
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
        response = self.client.put(uri, data=dumps(request_data))
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
        response = self.client.patch(uri, data=dumps(request_data))
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
        response = self.client.patch(uri, data=dumps(request_data))
        self.assert_response(response, 404)

    def test_datadog(self):
        uri = "/api/person"
        response = self.client.get(uri)
        self.assert_response(response, 200)
        assert_that(response.headers["microcosm.flask.requests"], is_(equal_to("['operation:person.search.v1', 'method:GET', 'func:search', 'status_code:200', 'result:success']")))
