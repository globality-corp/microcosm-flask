"""
An end-user message in a chatroom.

"""
from dataclasses import dataclass
from uuid import UUID


@dataclass
class Encryptable:
    id: UUID
    value: str | None = None
    other_value: str | None = None

    # # encryption support
    # __encrypted_identifier__ = "encrypted_chatroom_message_id"
    # __encrypted_relationship__ = "encrypted_chatroom_message"
    # __encryption_context_key__ = "client_id"
    __plaintext__ = "value"

    @property
    def plaintext(self) -> str:
        return getattr(self, self.__plaintext__)
