"""
Linking tests.

"""
from hamcrest import assert_that, equal_to, is_
from microcosm.api import create_object_graph

from microcosm_flask.linking import Link, Links
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


def test_link_to_dict():
    link = Link(
        href="href",
    )
    assert_that(link.to_dict(), is_(equal_to({
        "href": "href",
    })))


def test_typed_link_to_dict():
    link = Link(
        href="href",
        type="type",
    )
    assert_that(link.to_dict(), is_(equal_to({
        "href": "href",
        "type": "type",
    })))


def test_templated_link_to_dict():
    link = Link(
        href="href",
        templated=True,
    )
    assert_that(link.to_dict(), is_(equal_to({
        "href": "href",
        "templated": True,
    })))


def test_link_for_operation():
    graph = create_object_graph(name="example", testing=True)
    ns = Namespace(subject="foo")

    @graph.route(ns.collection_path, Operation.Search, ns)
    def func():
        pass

    with graph.app.test_request_context():
        link = Link.for_(Operation.Search, ns)
        assert_that(link.href, is_(equal_to("http://localhost/api/foo")))


def test_link_for_operation_without_namespace():
    graph = create_object_graph(name="example", testing=True)
    ns = Namespace(subject="foo")

    @graph.route(ns.collection_path, Operation.Search, ns)
    def func():
        pass

    with graph.app.test_request_context():
        link = Link.for_(Operation.Search, ns)
        assert_that(link.href, is_(equal_to("http://localhost/api/foo")))


def test_link_for_operation_with_query_string():
    graph = create_object_graph(name="example", testing=True)
    ns = Namespace(subject="foo")

    @graph.route(ns.collection_path, Operation.Search, ns)
    def func():
        pass

    with graph.app.test_request_context():
        link = Link.for_(Operation.Search, ns, qs=dict(bar="baz"))
        assert_that(link.href, is_(equal_to("http://localhost/api/foo?bar=baz")))


def test_link_for_operation_templated():
    graph = create_object_graph(name="example", testing=True)
    ns = Namespace(subject="foo")

    @graph.route(ns.instance_path, Operation.Retrieve, ns)
    def func():
        pass

    with graph.app.test_request_context():
        link = Link.for_(Operation.Retrieve, ns, allow_templates=True)
        assert_that(link.href, is_(equal_to("http://localhost/api/foo/{}".format("{foo_id}"))))


def test_links_empty():
    links = Links()
    assert_that(links.to_dict(), is_(equal_to({})))


def test_links_init():
    links = Links(
        foo=Link("foo"),
        bar=Link("bar"),
    )
    assert_that(links.to_dict(), is_(equal_to({
        "foo": {
            "href": "foo",
        },
        "bar": {
            "href": "bar",
        },
    })))


def test_links_init_list():
    links = Links(
        foo=[
            Link("bar"),
            Link("baz"),
        ]
    )
    assert_that(links.to_dict(), is_(equal_to({
        "foo": [{
            "href": "bar",
        }, {
            "href": "baz",
        }],
    })))


def test_links_as_item():
    links = Links()
    links["foo"] = Link("foo")
    links["bar"] = Link("bar")

    assert_that(links.to_dict(), is_(equal_to({
        "foo": {
            "href": "foo",
        },
        "bar": {
            "href": "bar",
        },
    })))
