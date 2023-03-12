"""
实体类，便于后续维护
"""
import copy
import inspect
from typing import get_origin, get_args, _GenericAlias, List

from app.main.utils import object_util


class Basic(dict):

    def __init__(self, *args, **kwargs):

        dict.__init__(self, **kwargs)
        self._reset_attribute()

        pass
        # self.__dict__ = copy.deepcopy({k: v for k, v in kwargs.items() if not k.startswith('__')})

    def __getattr__(self, *args, **kwargs):  # real signature unknown
        # 如果相关对象未定义，那么会进入该方法，返回默认值
        return self.get(args[0],None)

    # def __getattribute__(self, *args, **kwargs):  # real signature unknown
    #     return self.get(args[0],None)
    def __setattr__(self, key, value):
        self[key] = value

    def _reset_attribute(self):
        annotations: dict = self.__annotations__
        for key, tp in annotations.items():
            # 判断是否为基础类型
            if object_util.is_basic_type(tp) is True:
                continue
            if isinstance(tp, _GenericAlias):
                out_type = get_origin(annotations[key])
                inner_types = get_args(annotations[key])
                # List[str] or List[int] or List[float] or List[bool]
                if out_type == list:
                    if (object_util.is_basic_type(inner_types[0])):
                        continue
                    values = self.get(key,None)

                    if values is None:
                        continue
                    new_values = [inner_types[0](**value) for value in values]
                    self[key] = new_values
            else:
                continue

    #
    def __call__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        instance = super().__call__(*args, **kwargs)
        instance.__dict__ = copy.deepcopy({k: v for k, v in self.__dict__.items() if not k.startswith('__')})

    @classmethod
    def dict_to_obj(cls, dict_obj):
        entity = cls()
        entity.__dict__ = dict_obj
        return entity

    @classmethod
    def dict_to_obj_list(cls, dict_obj_list):
        """
        list形式的转换
        :param dict_obj:
        :return:
        """
        entity_list = [cls.dict_to_obj(obj) for obj in dict_obj_list]
        return entity_list
