"""
实体类，便于后续维护
"""
import copy


class Basic(dict):

    def __init__(self, *args, **kwargs):
        dict.__init__(self, **kwargs)
        # self.__dict__ = copy.deepcopy({k: v for k, v in kwargs.items() if not k.startswith('__')})

    def __getattr__(self, *args, **kwargs):  # real signature unknown
        # 如果相关对象未定义，那么会进入该方法，返回默认值
        return None


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
