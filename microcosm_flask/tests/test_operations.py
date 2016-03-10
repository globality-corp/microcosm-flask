"""
Operation tests.

"""
from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm.api import create_object_graph
from microcosm_flask.naming import collection_path_for
from microcosm_flask.operations import Operation


def test_operation_naming():
    """
    Operation naming works.

    """
    operation_name = Operation.Search.name_for("foo")
    assert_that(operation_name, is_(equal_to("foo.search")))


def test_operation_url_for():
    """
    Operations can resolve themselves via Flask's `url_for`.

    """
    graph = create_object_graph(name="example", testing=True)

    @graph.route(collection_path_for("foo"), Operation.Search, "foo")
    def search_foo():
        pass

    with graph.app.test_request_context():
        url = Operation.Search.url_for("foo")
        assert_that(url, is_(equal_to("/api/foo")))


def test_operation_href_for():
    """
    Operations can resolve themselves as fully expanded hrefs.

    """
    graph = create_object_graph(name="example", testing=True)

    @graph.route(collection_path_for("foo"), Operation.Search, "foo")
    def search_foo():
        pass

    with graph.app.test_request_context():
        url = Operation.Search.href_for("foo")
        assert_that(url, is_(equal_to("http://localhost/api/foo")))
