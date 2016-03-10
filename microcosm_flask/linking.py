"""
HAL JSON link modeling.

HAL JSON defines a simple-yet-powerful extension to plain old JSON that allows
resources to link to each other, enabling HATEOAS and the full power of REST.

See: https://tools.ietf.org/html/draft-kelly-json-hal-07

"""
from werkzeug.routing import BuildError

from microcosm_flask.operations import Operation


class Links(object):
    """
    A collection of links organized by relation name.

    """
    def __init__(self, links=None, **kwargs):
        self.links = links or {}
        for key, value in kwargs.items():
            self[key] = value

    def __getitem__(self, name):
        return self.links[name]

    def __setitem__(self, name, value):
        self.links[name] = value

    def to_dict(self):
        def encode(value):
            if isinstance(value, list):
                return [item.to_dict() for item in value]
            else:
                return value.to_dict()

        return {
            name: encode(value)
            for name, value in self.links.items()
        }


class Link(object):
    """
    A single link for a relation name.

    """
    def __init__(self, href, type=None, templated=False):
        self.href = href
        self.type = type
        self.templated = templated

    def to_dict(self):
        dct = {
            "href": self.href,
        }
        if self.type is not None:
            dct["type"] = self.type
        if self.templated:
            dct["templated"] = True
        return dct

    @classmethod
    def for_(cls, operation, obj, qs=None, type=None, allow_templates=False, **kwargs):
        """
        Create a link to an operation on a resource object.

        Supports link templating if enabled by making a best guess as to the URI
        template construction.

        See also [RFC 6570]( https://tools.ietf.org/html/rfc6570).

        :param operation: the operation
        :param obj: the resource object, name, or class
        :param qs: an optional query string (e.g. for paging)
        :param type: an optional link type
        :param allow_templates: whether generated links are allowed to contain templates
        :param kwargs: optional endpoint expansion arguments (e.g. for URI parameters)
        :raises BuildError: if link templating is needed and disallowed
        """
        try:
            href, templated = operation.href_for(obj, qs=qs, **kwargs), False
        except BuildError as error:
            if not allow_templates:
                raise
            uri_templates = {
                argument: "{{{}}}".format(argument)
                for argument in error.suggested.arguments
            }
            kwargs.update(uri_templates)
            href, templated = operation.href_for(obj, qs=qs, **kwargs), True

        return cls(
            href=href,
            type=type,
            templated=templated,
        )
