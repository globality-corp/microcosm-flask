"""
Common formatting test code.

"""


def etag_for(md5_hash, spooky_hash):
    try:
        import spooky  # noqa: F401
        return spooky_hash
    except ImportError:
        return md5_hash
