"""
Hamcrest matching support for JSON responses.

"""
from json import dumps, loads

from hamcrest.core.base_matcher import BaseMatcher

from microcosm_flask.fields.uri_field import normalize_uri


def prettify(value):
    return dumps(
        value,
        sort_keys=True,
        indent=4,
        separators=(',', ': '),
    )


class JSON:
    """
    Dictionary wrapper with JSON pretty-printing for Hamcrest's description.

    """
    def __init__(self, dct):
        self.dct = dct

    def __getitem__(self, key):
        return self.dct[key]

    def get(self, key):
        return self.dct.get(key)

    def describe_to(self, description):
        description.append(prettify(self.dct))


def json_for(value):
    if not isinstance(value, (dict, list)):
        value = loads(value)
    return JSON(value)


class JSONMatcher(BaseMatcher):
    """
    Hamcrest matcher of a JSON encoded resource.

    Subclasses must define `_matcher` and invoke `assert_that` within a request
    context to ensure that Flask's `url_for` can be resolved.

    Example:

        with graph.app.test_request_context():
           assert_that(json(response.data), matches_myresource(expected))

    """
    def __init__(self, resource):
        self.resource = resource
        self.schema = self.schema_class()
        self.expected = self.schema.dump(self.resource).data

    @property
    def schema_class(self):
        raise NotImplementedError

    def describe_to(self, description):
        description.append_text("expected {}".format(prettify(self.expected)))


class URIMatcher(BaseMatcher):
    """
    Hamcrest matcher for comparing URIs by canonicalizing them first.

    Example:

        with graph.app.test_request_context():
           assert_that(uri, matches_uri("https://canonical.url.com/path?a=1&b=2"))

    """
    def __init__(self, uri):
        self.uri = uri

    def _matches(self, item):
        if not isinstance(item, str):
            return False

        return normalize_uri(item) == normalize_uri(self.uri)

    def describe_to(self, description):
        description.append_text("expected URI: {}".format(self.uri))


def matches_uri(uri):
    return URIMatcher(uri)
