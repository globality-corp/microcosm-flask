"""
A URI valued (and normalized) field.

"""
from operator import itemgetter

from marshmallow.fields import Field, ValidationError
from rfc3986 import uri_reference


DEFAULT_PORTS = {
    "http": 80,
    "https": 443,
}


def normalize_uri(uri):
    """
    Normalize a URI (and return a string)

    """
    return normalize_uri_result(uri).unsplit()


def normalize_uri_result(uri):
    """
    Normalize a URI (And return a URIResult)

    """
    ref = uri_reference(uri).normalize()

    return ref._replace(
        authority=normalize_uri_authority(ref),
        query=normalize_uri_query(ref),
        path=normalize_uri_path(ref),
    )


def normalize_uri_query(ref):
    if not ref.query:
        return ref.query

    return "&".join([
        "=".join(term)
        for term
        in sorted(
            [
                term.split("=", 1)
                for term in ref.query.split("&")
            ],
            key=itemgetter(0),
        )
    ])


def normalize_uri_path(ref):
    if not ref.path:
        return ref.path
    return ref.path.rstrip("/")


def normalize_uri_authority(ref):
    if not ref.port:
        return ref.authority

    if DEFAULT_PORTS[ref.scheme] == int(ref.port):
        return ref.host

    return ref.authority


class URIField(Field):
    """
    Marshmallow field for a normalized URI.

    """
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return self.normalize(value)

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        return self.normalize(value)

    def normalize(self, value):
        result = normalize_uri_result(value)
        if not result.scheme:
            raise ValidationError("URI scheme is required for: {}".format(value))
        if not result.authority:
            raise ValidationError("URI authority is required for: {}".format(value))
        return result.unsplit()
