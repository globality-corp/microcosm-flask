"""
Test the discovery endpoint.

"""
from json import loads

from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm.api import create_object_graph
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


def test_discovery():
    graph = create_object_graph(name="example", testing=True)
    graph.use("discovery_convention")

    ns = Namespace("foo")

    @graph.route(ns.collection_path, Operation.Search, ns)
    def search_foo():
        pass

    client = graph.flask.test_client()

    response = client.get("/api")
    assert_that(response.status_code, is_(equal_to(200)))
    data = loads(response.get_data().decode("utf-8"))
    assert_that(data, is_(equal_to({
        "_links": {
            "search": [{
                "href": "http://localhost/api/foo?offset=0&limit=20",
                "type": "foo",
            }],
            "self": {
                "href": "http://localhost/api?offset=0&limit=20",
            },
        }
    })))
