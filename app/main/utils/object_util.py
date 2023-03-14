import copy
import importlib
import logging as log


def copy_obj(obj):
    return copy.copy(obj)

def get_method(obj):

    return {k:v for k,v in obj.__dict__.items() if callable(v)}


def get_method_by_path(path):
    p, m = path.rsplit('.', 1)
    log.info("module {} m {}".format(p, m))
    method = getattr(importlib.import_module(p),
                     m, None)
    return method


def is_basic_type(tp):
    return tp == int or tp == float or tp == bool or tp == str or tp == any


def is_basic_obj(obj):
    return isinstance(obj, int) \
           or isinstance(obj, float) \
           or isinstance(obj, bool) \
           or isinstance(obj, str)
