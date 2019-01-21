from collections import MutableMapping
from typing import Union

from pymongo.collection import Collection
from pymongo.cursor import Cursor


class BaseMongoCollection(Collection):
    def __init__(self, mongo_client, db_name: str, col_name: str, cache_keys: Union[dict, None] = None):
        super().__init__(mongo_client.get_database(db_name), col_name)
        self._cache = {}
        if cache_keys is not None:
            for k in cache_keys:
                self.init_cache(k)

    def init_cache(self, cache_key):
        self._cache[cache_key] = {}

    def set_cache(self, cache_key, item_key, item):
        if cache_key not in self._cache:
            self.init_cache(cache_key)

        self._cache[cache_key][item_key] = item

    def get_cache(self, cache_key, item_key, result_acquire_method=None):
        if result_acquire_method is None:
            result_acquire_method = self.find_one

        if cache_key not in self._cache:
            self.init_cache(cache_key)

        if item_key not in self._cache[cache_key]:
            data = result_acquire_method({cache_key: item_key})

            if isinstance(data, Cursor):
                data = list(data)

            self.set_cache(cache_key, item_key, data)

        return self._cache[cache_key][item_key]


class DictLikeMapping(MutableMapping):
    @classmethod
    def get_none(cls, org_dict):
        return None if org_dict is None else cls(org_dict)

    def __init__(self, org_dict):
        if org_dict is None:
            self._dict = {}
        else:
            self._dict = dict(org_dict)

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return str(self._dict)

    def __getnewargs__(self):
        return self._dict

    @property
    def __dict__(self):
        return self._dict
