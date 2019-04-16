from microcosm_flask.conventions.crud_adapter import CRUDStoreAdapter


class EncryptableCRUDStoreAdapter(CRUDStoreAdapter):
    """
    Adapt the CRUD conventions callbacks to the `EncryptableStore` interface.

    """

    def update_and_reencrypt(self, **kwargs):
        """
        Support re-encryption by enforcing that every update triggers a
        new encryption call, even if the the original call does not update
        the encrypted field.

        """
        encrypted_field_name = self.store.model_class.__plaintext__

        id_ = kwargs[self.identifier_key]
        current_model = self.store.retrieve(id_)
        current_value = current_model.plaintext

        null_update = (
            # Check if the update is for the encrypted field, and if it's explicitly set to null
            encrypted_field_name in kwargs
            and kwargs.get(encrypted_field_name) is None
        )
        new_value = kwargs.pop(self.store.model_class.__plaintext__, None)
        use_new_value = new_value is not None or null_update

        updated_value = new_value if use_new_value else current_value

        model_kwargs = {
            self.identifier_key: id_,
            encrypted_field_name: updated_value,
            **kwargs,
        }

        return super().update(
            **model_kwargs,
        )
