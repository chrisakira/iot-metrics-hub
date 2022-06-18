"""
Value Object Module for Application
Version: 1.0.0
"""
import json

from application import helper


def remove_null_params(self_dict: dict):
    final_dict = {}
    for k, v in self_dict.items():
        if v is not None:
            final_dict[k] = v
    return final_dict


class AbstractVO:
    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return self.to_json()

    def to_dict(self, force_str=False):
        return helper.to_dict(self, force_str)

    def to_json(self):
        return json.dumps(self.to_dict(force_str=False))

    def to_api_response(self, convert_to_utc=True):
        """
        Apply iso format to result
        """
        helper.convert_object_dates_to_iso_utc(self)
        self_dict = helper.to_dict(self, force_str=False)
        return remove_null_params(self_dict)

    def __getitem__(self, n):
        """
        Permite o objeto ser iterado
        :param n:
        :return:
        """
        count = len(self.__dict__)
        items = list(self.__dict__)
        if n >= count:
            raise IndexError("Object has no item %s" % (n,))
        else:
            return items[n]

    def get(self, k, d=None):
        """ Object.get(k[,d]) -> Object[k] if k in Object, else d.  d defaults to None. """
        return self.__dict__[k] if k in self.__dict__.keys() else d

    def keys(self):
        """ Object.keys() -> a set-like object providing a view on Object's keys """
        return self.__dict__.keys()

    def values(self):
        """ Object.values() -> an object providing a view on Object's values """
        return self.__dict__.values()
