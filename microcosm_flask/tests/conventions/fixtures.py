"""
Testing fixtures (e.g. for CRUD).

"""
from uuid import uuid4

from marshmallow import fields, Schema

from microcosm_flask.linking import Links, Link
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


class Address(object):
    def __init__(self, id, person_id, address_line):
        self.id = id
        self.person_id = person_id
        self.address_line = address_line


class Person(object):
    def __init__(self, id, first_name, last_name):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name


class NewAddressSchema(Schema):
    addressLine = fields.Str(attribute="address_line", required=True)


class NewPersonSchema(Schema):
    firstName = fields.Str(attribute="first_name", required=True)
    lastName = fields.Str(attribute="last_name", required=True)


class NewPersonBatchSchema(Schema):
    items = fields.List(fields.Nested(NewPersonSchema))


class UpdatePersonSchema(Schema):
    firstName = fields.Str(attribute="first_name")
    lastName = fields.Str(attribute="last_name")


class AddressSchema(NewAddressSchema):
    id = fields.UUID(required=True)
    _links = fields.Method("get_links", dump_only=True)

    def get_links(self, obj):
        links = Links()
        links["self"] = Link.for_(
            Operation.Retrieve,
            ns=Namespace(
                subject=Address,
                path=Namespace(
                    subject=Person,
                ).instance_path,
            ),
            person_id=obj.person_id,
            address_id=obj.id,
            )
        return links.to_dict()


class PersonSchema(NewPersonSchema):
    id = fields.UUID(required=True)
    _links = fields.Method("get_links", dump_only=True)

    def get_links(self, obj):
        links = Links()
        links["self"] = Link.for_(Operation.Retrieve, Person, person_id=obj.id)
        return links.to_dict()


class PersonLookupSchema(Schema):
    family_member = fields.Boolean(required=False)


class PersonBatchSchema(NewPersonSchema):
    items = fields.List(fields.Nested(PersonSchema))


ADDRESS_ID_1 = uuid4()
PERSON_ID_1 = uuid4()
PERSON_ID_2 = uuid4()
PERSON_ID_3 = uuid4()
PERSON_1 = Person(PERSON_ID_1, "Alice", "Smith")
PERSON_2 = Person(PERSON_ID_2, "Bob", "Jones")
PERSON_3 = Person(PERSON_ID_3, "Charlie", "Smith")
ADDRESS_1 = Address(ADDRESS_ID_1, PERSON_ID_1, "21 Acme St., San Francisco CA 94110")


def address_retrieve(id, person_id, address_id):
    return ADDRESS_1


def address_search(person_id, offset, limit, list_param=None, enum_param=None):
    if list_param is None or enum_param is None:
        return [ADDRESS_1], 1, dict(person_id=person_id)
    return Address(ADDRESS_ID_1,
                   PERSON_ID_1,
                   ",".join(list_param) + str(len(list_param)) + enum_param.value), 1, dict(person_id=person_id)


def person_create(**kwargs):
    return Person(id=PERSON_ID_2, **kwargs)


def person_search(offset, limit):
    return [PERSON_1], 1


def person_update_batch(items):
    return dict(
        items=[
            person_create(**item)
            for item in items
        ]
    )


def person_retrieve(person_id, family_member=None):
    if family_member:
        return PERSON_3
    elif person_id == PERSON_ID_1:
        return PERSON_1
    else:
        return None


def person_delete(person_id):
    return person_id == PERSON_ID_1


def person_replace(person_id, **kwargs):
    return Person(id=person_id, **kwargs)


def person_update(person_id, **kwargs):
    if person_id == PERSON_ID_1:
        for key, value in kwargs.items():
            setattr(PERSON_1, key, value)
        return PERSON_1
    else:
        return None
