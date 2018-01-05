"""
Adapter between conventional crud functions and the `microcosm_postgres.store.Store` interface.

"""
from microcosm_flask.naming import name_for


class CRUDStoreAdapter:
    """
    Adapt the CRUD conventions callbacks to the `Store` interface.

    Does NOT impose transactions; use the `microcosm_postgres.context.transactional` decorator.

    """
    def __init__(self, graph, store):
        self.graph = graph
        self.store = store

    @property
    def identifier_key(self):
        return "{}_id".format(name_for(self.store.model_class))

    def create(self, **kwargs):
        model = self.store.model_class(**kwargs)
        return self.store.create(model)

    def delete(self, **kwargs):
        identifier = kwargs.pop(self.identifier_key)
        return self.store.delete(identifier)

    def replace(self, **kwargs):
        identifier = kwargs.pop(self.identifier_key)
        model = self.store.model_class(id=identifier, **kwargs)
        return self.store.replace(identifier, model)

    def retrieve(self, **kwargs):
        identifier = kwargs.pop(self.identifier_key)
        return self.store.retrieve(identifier)

    def search(self, offset, limit, **kwargs):
        items = self.store.search(offset=offset, limit=limit, **kwargs)
        count = self.store.count(**kwargs)
        return items, count

    def count(self, offset=None, limit=None, **kwargs):
        count = self.store.count(**kwargs)
        return count

    def update(self, **kwargs):
        identifier = kwargs.pop(self.identifier_key)
        model = self.store.model_class(id=identifier, **kwargs)
        return self.store.update(identifier, model)

    def update_batch(self, **kwargs):
        """
        Simplistic batch update operation implemented in terms of `replace()`.

        Assumes that:

         - Request and response schemas contains lists of items.
         - Request items define a primary key identifier
         - The entire batch succeeds or fails together.

        """
        items = kwargs.pop("items")

        def transform(item):
            """
            Transform the dictionary expected for replace (which uses the URI path's id)
            into the resource expected from individual resources (which uses plain id).

            """
            item[self.identifier_key] = item.pop("id")
            return item

        return dict(
            items=[
                self.replace(**transform(item))
                for item in items
            ],
        )
