import logging

log = logging.getLogger(__name__)


def to_string(input: any):
    """
    对象转字符串
    :param input:
    :return:
    """
    if isinstance(input, dict):
        item_list = ["{}={}".format(k, v) for k, v in input.items()]
        return ",".join(item_list)
