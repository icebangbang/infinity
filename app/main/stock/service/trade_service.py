"""
交易节点相关实现
"""
from app.main.db.mongo import db


# cost 成本
# positions_num 持仓数量


def position_query(**kwargs) -> str:
    """
    查询指定holder_id，position_id，task_group_name的持仓情况
    :param kwargs:
    :return:
    """
    holder_id = kwargs['holderId']
    position_id = kwargs['positionId']
    task_group_name = kwargs['taskGroupName']

    position_detail = db['trade_position_detail']
    detail = position_detail.find_one(dict(position_id=position_id,
                                           trade_style=task_group_name,
                                           holder_id=holder_id))
    if detail is None:
        return "没有持仓"

    positions_num = detail.get('positions_num', 0)

    if (positions_num == 0):
        return "没有持仓"
    return "已有持仓"


def position_strategy_query(holderId, positionId, taskGroupName, **kwargs):
    """
    持仓策略查询,平仓，减仓，加仓
    :param holderId:
    :param positionId:
    :param taskGroupName:
    :param kwargs:
    :return:
    """

    # 平仓判断
    # 1. 盈利符合预期
    # 2. 板块短期趋势已经达到拐点

    # 减仓判断
    # 1. 2b结构

    # 加仓判断
    # 1.下行趋势，之前的交易日已有满足开仓买入情况，后续突然出现大幅下杀，可以加仓




    pass
