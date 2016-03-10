"""
A naming convention and discovery mechanism for HTTP endpoints.

Operations provide a naming convention for references between endpoints,
allowing easy construction of links or audit trails for external consumption.

"""
from collections import namedtuple
from urllib import urlencode
from urlparse import urljoin

from enum import Enum, unique
from flask import request, url_for

from microcosm_flask.naming import name_for


# metadata for an operation
OperationInfo = namedtuple("OperationInfo", ["name", "method"])


@unique
class Operation(Enum):
    """
    An enumerated set of operation types, which know how to resolve themselves into
    URLs and hrefs.

    """
    # discovery operation
    Discover = OperationInfo("discover", "GET")

    # collection operations
    Search = OperationInfo("search", "GET")
    Create = OperationInfo("create", "POST")

    # instance operations
    Retrieve = OperationInfo("retrieve", "GET")
    Delete = OperationInfo("delete", "DELETE")
    Replace = OperationInfo("replace", "PUT")
    Update = OperationInfo("update", "PATCH")

    def name_for(self, obj):
        """
        Generate an operation name in the scope of the resource.

        This naming convention matches how Flask blueprints routes are resolved
        (assuming that the blueprint and resources share the same name).

        Example: `foo.search`
        """
        return "{}.{}".format(name_for(obj), self.value.name)

    def url_for(self, obj, **kwargs):
        """
        Construct a URL for an operation against a resource.

        :param kwargs: additional arguments for URL path expansion

        """
        return url_for(self.name_for(obj), **kwargs)

    def href_for(self, obj, qs=None, **kwargs):
        """
        Construct an full href for an operation against a resource.

        :parm qs: the query string dictionary, if any
        :param kwargs: additional arguments for path expansion
        """
        return "{}{}".format(
            urljoin(request.url_root, self.url_for(obj, **kwargs)),
            "?{}".format(urlencode(qs)) if qs else "",
        )
