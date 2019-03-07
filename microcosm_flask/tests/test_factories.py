"""
Factory tests.

"""
from flask import Flask
from hamcrest import assert_that, instance_of, is_
from microcosm.api import create_object_graph


def test_configure_flask():
    """
    Should create the `Flask` application.

    """
    graph = create_object_graph(name="example", testing=True)
    assert_that(graph.app, is_(instance_of(Flask)))
