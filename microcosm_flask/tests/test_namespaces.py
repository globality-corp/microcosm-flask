"""
Namespace tests.

"""
from hamcrest import (
    assert_that,
    equal_to,
    is_,
    none,
)
from mock import Mock

from microcosm.api import create_object_graph
from microcosm_flask.matchers import matches_uri
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


def test_endpoint_for():
    """
    Simple (subject-only) endpoint naming works.

    """
    ns = Namespace(subject="foo")
    endpoint = ns.endpoint_for(Operation.Search)
    assert_that(endpoint, is_(equal_to("foo.search.v1.uuid")))


def test_operation_naming_relation():
    """
    Complext (subject+object) endpoint naming works.

    """
    ns = Namespace(subject="foo", object_="bar")
    endpoint = ns.endpoint_for(Operation.SearchFor)
    assert_that(endpoint, is_(equal_to("foo.search_for.bar.v1.uuid")))


def test_parse_endpoint():
    """
    Simple (subject-only) endpoints can be parsed.

    """
    operation, ns = Namespace.parse_endpoint("foo.search.v1.uuid")
    assert_that(operation, is_(equal_to(Operation.Search)))
    assert_that(ns.subject, is_(equal_to("foo")))
    assert_that(ns.object_, is_(none()))


def test_parse_endpoint_relation():
    """
    Complex (subject+object) endpoints can be parsed.

    """
    operation, ns = Namespace.parse_endpoint("foo.search_for.bar.v1.uuid")
    assert_that(operation, is_(equal_to(Operation.SearchFor)))
    assert_that(ns.subject, is_(equal_to("foo")))
    assert_that(ns.object_, is_(equal_to("bar")))


def test_parse_endpoint_swagger():
    """
    Versioned discovery endpoint can be parsed.

    """
    operation, ns = Namespace.parse_endpoint("swagger.discover.v2.uuid")
    assert_that(operation, is_(equal_to(Operation.Discover)))
    assert_that(ns.subject, is_(equal_to("swagger")))
    assert_that(ns.version, is_(equal_to("v2")))
    assert_that(ns.object_, is_(none()))


def test_operation_url_for():
    """
    Operations can resolve themselves via Flask's `url_for`.

    """
    graph = create_object_graph(name="example", testing=True)
    ns = Namespace(subject="foo")

    @graph.route(ns.collection_path, Operation.Search, ns)
    def search_foo():
        pass

    with graph.app.test_request_context():
        url = ns.url_for(Operation.Search)
        assert_that(url, is_(equal_to("http://localhost/api/foo")))


def test_operation_url_for_internal():
    """
    Operations can resolve themselves via Flask's `url_for` and get internal URIs.

    """
    graph = create_object_graph(name="example", testing=True)
    ns = Namespace(subject="foo")

    @graph.route(ns.collection_path, Operation.Search, ns)
    def search_foo():
        pass

    with graph.app.test_request_context():
        url = ns.url_for(Operation.Search, _external=False)
        assert_that(url, is_(equal_to("/api/foo")))


def test_operation_href_for():
    """
    Operations can resolve themselves as fully expanded hrefs.

    """
    graph = create_object_graph(name="example", testing=True)
    ns = Namespace(subject="foo")

    @graph.route(ns.collection_path, Operation.Search, ns)
    def search_foo():
        pass

    with graph.app.test_request_context():
        url = ns.href_for(Operation.Search)
        assert_that(url, is_(equal_to("http://localhost/api/foo")))


def test_operation_href_for_qs():
    """
    Operations can resolve themselves as fully expanded hrefs with
    custom query string parameter.

    """
    graph = create_object_graph(name="example", testing=True)
    ns = Namespace(subject="foo")

    @graph.route(ns.collection_path, Operation.Search, ns)
    def search_foo():
        pass

    with graph.app.test_request_context():
        url = ns.href_for(Operation.Search, offset=0, limit=10, qs=dict(foo="bar"))
        assert_that(url, matches_uri("http://localhost/api/foo?offset=0&limit=10&foo=bar"))


def test_namespace_accepts_controller():
    """
    Namespaces may optionally contain a controller.

    """
    graph = create_object_graph(name="example", testing=True)
    controller = Mock()
    ns = Namespace(subject="foo", controller=controller)

    @graph.route(ns.collection_path, Operation.Search, ns)
    def search_foo():
        pass

    with graph.app.test_request_context():
        url = ns.href_for(Operation.Search)
        assert_that(url, is_(equal_to("http://localhost/api/foo")))
        url = ns.url_for(Operation.Search)
        assert_that(url, is_(equal_to("http://localhost/api/foo")))
        assert_that(ns.controller, is_(equal_to(controller)))


def test_qualified_operation_href_for():
    """
    Qualified operations add to the URI.

    """
    graph = create_object_graph(name="example", testing=True)
    ns = Namespace(subject="foo", qualifier="bar", version="v1")

    @graph.route(ns.collection_path, Operation.Search, ns)
    def search_foo():
        pass

    @graph.route(ns.instance_path, Operation.Retrieve, ns)
    def get_foo(foo_id):
        pass

    with graph.app.test_request_context():
        url = ns.href_for(Operation.Retrieve, foo_id="baz")
        assert_that(url, is_(equal_to("http://localhost/api/v1/bar/foo/baz")))
