"""
A naming convention and discovery mechanism for HTTP endpoints.

Operations provide a naming convention for references between endpoints,
allowing easy construction of links or audit trails for external consumption.

"""
from collections import namedtuple
from enum import Enum, unique


# metadata for an operation
OperationInfo = namedtuple("OperationInfo", ["name", "method", "pattern", "default_code"])


# NB: Namespace.parse_endpoint requires that operation is the second argument
NODE_PATTERN = "{subject}.{operation}.{version}"
EDGE_PATTERN = "{subject}.{operation}.{object_}.{version}"


@unique
class Operation(Enum):
    """
    An enumerated set of operation types, which know how to resolve themselves into
    URLs and hrefs.

    """
    # discovery operation
    Discover = OperationInfo("discover", "GET", NODE_PATTERN, 200)

    # collection operations
    Search = OperationInfo("search", "GET", NODE_PATTERN, 200)
    Count = OperationInfo("count", "HEAD", NODE_PATTERN, 200)
    Create = OperationInfo("create", "POST", NODE_PATTERN, 201)
    UpdateBatch = OperationInfo("update_batch", "PATCH", NODE_PATTERN, 200)
    CreateCollection = OperationInfo("create_collection", "POST", NODE_PATTERN, 200)
    SavedSearch = OperationInfo("saved_search", "POST", NODE_PATTERN, 200)

    # instance operations
    Retrieve = OperationInfo("retrieve", "GET", NODE_PATTERN, 200)
    Delete = OperationInfo("delete", "DELETE", NODE_PATTERN, 204)
    Replace = OperationInfo("replace", "PUT", NODE_PATTERN, 200)
    Update = OperationInfo("update", "PATCH", NODE_PATTERN, 200)
    Alias = OperationInfo("alias", "GET", NODE_PATTERN, 302)

    # relation operations
    CreateFor = OperationInfo("create_for", "POST", EDGE_PATTERN, 201)
    DeleteFor = OperationInfo("delete_for", "DELETE", EDGE_PATTERN, 204)
    ReplaceFor = OperationInfo("replace_for", "PUT", EDGE_PATTERN, 200)
    RetrieveFor = OperationInfo("retrieve_for", "GET", EDGE_PATTERN, 200)
    SearchFor = OperationInfo("search_for", "GET", EDGE_PATTERN, 200)
    UpdateFor = OperationInfo("update_for", "PATCH", EDGE_PATTERN, 200)

    # file upload operations
    Upload = OperationInfo("upload", "POST", NODE_PATTERN, 200)
    UploadFor = OperationInfo("upload_for", "POST", EDGE_PATTERN, 200)

    # ad hoc operations
    Command = OperationInfo("command", "POST", NODE_PATTERN, 200)
    Query = OperationInfo("query", "GET", NODE_PATTERN, 200)

    @classmethod
    def from_name(cls, name):
        for operation in cls:
            if operation.value.name.lower() == name.lower():
                return operation
        else:
            raise ValueError(name)

    @property
    def endpoint_pattern(self):
        """
        Convert the operation's pattern into a regex matcher.

        """
        parts = self.value.pattern.split(".")
        return "[.]".join(
            "(?P<{}>[^.]*)".format(part[1:-1])
            for part in parts
        )
