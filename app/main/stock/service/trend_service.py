"""
趋势相关服务
"""
from app.main.db.mongo import db
from app.main.stock import constant
from app.main.stock.company import Company


def save_stock_trend_with_company(company: Company):
    """
    保存当前和过去的趋势数据
    :return:
    """
    name = company.name
    code = company.code
    features = company.features

    trade_point = db['trade_point']

    entity = {}
    # 当前底分型趋势的斜率
    current_bot_type_slope = features[constant.current_bot_type_slope]
    # 当前顶分型趋势的斜率
    current_top_type_slope = features[constant.current_top_type_slope]
    # 当前底分型趋势的交易日数
    current_bot_trend_size = features[constant.current_bot_trend_size]
    entity['current_trend'] = {}

    trend = None
    if current_bot_type_slope > 0 and current_top_type_slope > 0:
        trend = "up"
    if current_bot_type_slope < 0 and current_top_type_slope < 0:
        trend = "down"
    if current_bot_type_slope < 0 and current_top_type_slope < 0:
        trend = "down"
    if current_bot_type_slope < 0 and current_top_type_slope < 0:
        trend = "down"


def save_stock_trend(code, name, ):
    """
    保存当前和过去的趋势
    :return:
    """
    pass
