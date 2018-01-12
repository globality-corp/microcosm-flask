"""
Operation tests.

"""
from hamcrest import (
    assert_that,
    equal_to,
    is_,
)

from microcosm_flask.operations import Operation


def test_from_name():
    """
    Operations can be looked up by name.

    """
    assert_that(Operation.from_name("search"), is_(equal_to(Operation.Search)))
    assert_that(Operation.from_name("Create"), is_(equal_to(Operation.Create)))


def test_endpoint_pattern():
    """
    Operations define valid endpoint patterns.

    """
    assert_that(
        Operation.Discover.endpoint_pattern,
        is_(equal_to("(?P<subject>[^.]*)[.](?P<operation>[^.]*)[.](?P<version>[^.]*)[.](?P<identifier_type>[^.]*)")),
    )
    assert_that(
        Operation.Search.endpoint_pattern,
        is_(equal_to("(?P<subject>[^.]*)[.](?P<operation>[^.]*)[.](?P<version>[^.]*)[.](?P<identifier_type>[^.]*)")),
    )
    assert_that(
        Operation.SearchFor.endpoint_pattern,
        is_(equal_to("(?P<subject>[^.]*)[.](?P<operation>[^.]*)[.](?P<object_>[^.]*)[.](?P<version>[^.]*)[.](?P<identifier_type>[^.]*)")),
    )
