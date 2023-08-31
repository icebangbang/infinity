import os
import pkgutil
import importlib

chart_cls_dict = dict()
chart_instance_dict = dict()
path = os.path.split(os.path.realpath(__file__))[0]

# for importer_sql, modname, ispkg_sql in pkgutil.walk_packages(path=__path__,
#                                                               prefix=__name__ + '.',
#                                                               onerror=lambda x: None):
#     # exec('from ' + modname + ' import *')
#     name = modname.split(".")[-1]
#     chart_cls = getattr(importlib.import_module(modname),
#                         name, None)
#     chart_cls_dict[name] = chart_cls
#     chart_instance_dict[name] = chart_cls()
