from microcosm.api import binding

from microcosm_flask.tests.encryption.conventions.fixtures.encryptable_models import Encryptable


@binding("encryptable_store")
class EncryptableStore:

    def __init__(self, graph):
        pass

    def retrieve(self, id_):
        return Encryptable(
            id=id_,
            value="current_value",
            other_value="current_other_value",
        )

    def update(self, identifier, model):
        return model

    @property
    def model_class(self):
        return Encryptable
