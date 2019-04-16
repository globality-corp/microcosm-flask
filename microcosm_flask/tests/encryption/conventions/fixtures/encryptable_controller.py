"""
Encryptable controller.

"""
from microcosm.api import binding

from microcosm_flask.encryption.conventions.crud_adapter import EncryptableCRUDStoreAdapter
from microcosm_flask.namespaces import Namespace


@binding("encryptable_controller")
class EncryptableController(EncryptableCRUDStoreAdapter):

    def __init__(self, graph):
        super().__init__(graph, graph.encryptable_store)

        self.ns = Namespace(
            subject="encryptable",
            version="v1",
        )
