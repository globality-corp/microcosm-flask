"""
Common formatting test code.

"""


def etag_for(sha1_hash, spooky_hash):
    try:
        import spooky  # noqa: F401
        return spooky_hash
    except ImportError:
        return sha1_hash
