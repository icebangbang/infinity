
import copy
import importlib
import logging as log


def copy_obj(obj):
    return copy.copy(obj)

def get_method_by_path(path):
    p, m = path.rsplit('.', 1)
    log.info("module {} m {}".format(p, m))
    method = getattr(importlib.import_module(p),
                     m, None)
    return method