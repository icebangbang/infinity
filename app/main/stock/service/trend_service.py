"""
趋势相关服务
"""
from app.main.db.mongo import db
from app.main.stock import constant
from app.main.stock.company import Company
from app.main.stock.dao import stock_dao
from datetime import datetime


def save_stock_trend_with_company(company: Company, start_of_day: datetime):
    """
    保存当前和过去的趋势数据
    :return:
    """
    name = company.name
    code = company.code
    features = company.features

    trade_point_set = db['trade_point2']

    stock_detail = stock_dao.get_stock_detail_by_name(name)

    # 当前底分型趋势的斜率
    current_bot_type_slope = features[constant.current_bot_type_slope]
    # 当前顶分型趋势的斜率
    current_top_type_slope = features[constant.current_top_type_slope]
    # 当前底分型趋势的交易日数
    current_bot_trend_size = features[constant.current_bot_trend_size]
    current_top_trend_size = features[constant.current_top_trend_size]
    inf_l_point_date = features[constant.inf_l_point_date]
    inf_h_point_date = features[constant.inf_h_point_date]
    inf_l_point_value = features[constant.inf_l_point_value]
    inf_h_point_value = features[constant.inf_h_point_value]

    # todo 查找之前的趋势并判断趋势是否出现变化
    # 顶分型趋势
    # 底分型趋势
    # 任何趋势变化,就新增一条记录
    trend_change_scope = []
    trade_point_list = list(trade_point_set.find({"code": code,
                                                  "date":{"$lte":start_of_day}},
                                                 sort=[("date", -1),("_id",-1)]).limit(1))
    trade_point = None
    # 历史记录不为空,就要做更新
    if len(trade_point_list) > 0:
        trade_point = trade_point_list[0]
        inf_l_point_date_history = trade_point['inf_l_point_date']
        inf_h_point_date_history = trade_point['inf_h_point_date']
        if inf_l_point_date_history != inf_l_point_date:
            trend_change_scope.append(1)
        if inf_h_point_date_history != inf_h_point_date:
            trend_change_scope.append(2)

    if len(trend_change_scope) == 0 and trade_point is not None:
        trade_point['current_bot_trend_size'] = current_bot_trend_size
        trade_point['current_top_trend_size'] = current_top_trend_size
        trade_point['update'] = start_of_day
        trade_point['update_time'] = datetime.now()
        trade_point_set.update_one({"_id": trade_point["_id"]}, {"$set": trade_point})
        return
    elif trade_point is None:
        trend_change_scope = [1,2]

    trend = None
    # 上行
    if current_bot_type_slope > 0 and current_top_type_slope > 0:
        trend = "up"
    # 下行
    if current_bot_type_slope >= 0 and current_top_type_slope <= 0:
        trend = "convergence"
    # 收敛
    if current_bot_type_slope < 0 and current_top_type_slope < 0:
        trend = "down"
    # 放大 这个案例应该会比较少
    if current_bot_type_slope <= 0 and current_top_type_slope >=0:
        trend = "enlarge"

    entity = dict(
        date=start_of_day,
        is_in_use=1,
        current_bot_trend_size=current_bot_trend_size,
        current_top_trend_size=current_top_trend_size,
        current_top_type_slope = current_top_type_slope,
        current_bot_type_slope = current_bot_type_slope,
        trend=trend,  # 当前总体趋势
        prev_trend=trade_point['trend'] if trade_point is not None else None,  # 之前总体趋势
        inf_l_point_date=inf_l_point_date,  # 底分型趋势成立时间
        inf_h_point_date=inf_h_point_date,  # 顶分型趋势成立时间
        trend_change_scope=trend_change_scope,  # 趋势变化记录
        industry=stock_detail['industry'],  # 行业
        name=name,
        code=code,
        update= start_of_day,
        update_time = datetime.now(),
        inf_l_point_value=inf_l_point_value,
        inf_h_point_value=inf_h_point_value
    )
    trade_point_set.save(entity)
    if (trade_point):
        trade_point_set.update_one({"_id": trade_point["_id"]}, {"$set": {"is_in_use": 0}})


def save_stock_trend(code, name, ):
    """
    保存当前和过去的趋势
    :return:
    """
    pass
