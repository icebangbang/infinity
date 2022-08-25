"""
趋势相关服务
"""
from app.main.db.mongo import db
from app.main.stock import constant
from app.main.stock.company import Company
from app.main.stock.const import board_const
from app.main.stock.dao import stock_dao
from datetime import datetime
import pandas as pd
from app.main.utils import date_util
from app.main.utils.date_util import WorkDayIterator
import logging as log


def save_stock_trend_with_features(code, name, features, start_of_day: datetime):
    trend_point_set = db['trend_point']
    try:
        stock_detail = stock_dao.get_stock_detail_by_code(code)

        if stock_detail.get("industry", None) is None:
            return

        if features is None or len(features) == 0:
            return

        # 当前底分型趋势的斜率
        current_bot_type_slope = features[constant.current_bot_type_slope]
        # 当前顶分型趋势的斜率
        current_top_type_slope = features[constant.current_top_type_slope]
        # 当前底分型趋势的交易日数
        current_bot_trend_size = features[constant.current_bot_trend_size]
        prev_top_type_slope = features[constant.prev_top_type_slope]
        prev_bot_type_slope = features[constant.prev_bot_type_slope]
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
        trend_point_list = list(trend_point_set.find({"code": code,
                                                      "date": {"$lte": start_of_day}},
                                                     sort=[("date", -1), ("_id", -1)]).limit(2))
        trend_point = None
        # 历史记录不为空,就要做更新
        if len(trend_point_list) > 0:
            trend_point = trend_point_list[0]
            inf_l_point_date_history = trend_point['inf_l_point_date']
            inf_h_point_date_history = trend_point['inf_h_point_date']
            if inf_l_point_date_history != inf_l_point_date:
                trend_change_scope.append(1)
            if inf_h_point_date_history != inf_h_point_date:
                trend_change_scope.append(2)

        if len(trend_change_scope) == 0 and trend_point is not None:
            trend_point['current_bot_trend_size'] = current_bot_trend_size
            trend_point['current_top_trend_size'] = current_top_trend_size
            trend_point['update'] = start_of_day
            trend_point['update_time'] = datetime.now()

            # 当天的数据,对趋势进行更新
            if trend_point['date'] == date_util.get_start_of_day(datetime.now()) and \
                    trend_point['prev_trend'] is None and len(trend_point_list) > 1:
                trend_point['prev_trend'] = trend_point_list[1]['trend']

            trend_point_set.update_one({"_id": trend_point["_id"]}, {"$set": trend_point})
            return
        elif trend_point is None:
            trend_change_scope = [1, 2]

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
        if current_bot_type_slope <= 0 and current_top_type_slope >= 0:
            trend = "enlarge"

        entity = dict(
            date=start_of_day,
            is_in_use=1,
            current_bot_trend_size=current_bot_trend_size,
            current_top_trend_size=current_top_trend_size,
            current_top_type_slope=current_top_type_slope,
            current_bot_type_slope=current_bot_type_slope,
            prev_top_type_slope=prev_top_type_slope,
            prev_bot_type_slope=prev_bot_type_slope,
            trend=trend,  # 当前总体趋势
            prev_trend=trend_point['trend'] if trend_point is not None else None,  # 之前总体趋势
            inf_l_point_date=inf_l_point_date,  # 底分型趋势成立时间
            inf_h_point_date=inf_h_point_date,  # 顶分型趋势成立时间
            trend_change_scope=trend_change_scope,  # 趋势变化记录
            industry=stock_detail['industry'],  # 行业
            name=name,
            code=code,
            update=start_of_day,
            update_time=datetime.now(),
            inf_l_point_value=inf_l_point_value,
            inf_h_point_value=inf_h_point_value
        )
        trend_point_set.save(entity)
        if (trend_point):
            trend_point_set.update_one({"_id": trend_point["_id"]}, {"$set": {"is_in_use": 0}})
    except Exception as e:
        log.error(e, exc_info=1)


def save_stock_trend_with_company(company: Company, start_of_day: datetime):
    """
    保存当前和过去的趋势数据
    :return:
    """
    name = company.name
    code = company.code
    features = company.features

    save_stock_trend_with_features(code, name, features, start_of_day)


def get_trend_size_info(start, end):
    """
    获取各个趋势分组数据
    :return:
    """
    board_detail = db['board_detail']
    boards = list(board_detail.find({"type": 2}))
    board_dict = {board['board']: board['size'] for board in boards}

    result_list = []

    another_boards = list(board_detail.find({"board": {"$in": board_const.include}}))

    for date in WorkDayIterator(start, end):
        print(date)
        for another_board in another_boards:
            trend_point_set = db['trend_point']
            total = another_board['codes']
            r = list(trend_point_set.find(
                {"date": {"$lte": date},
                 "update": {"$gte": date}, "code": {"$in": total}}))
            if len(r) == 0: continue
            df = pd.DataFrame(r)
            series = df.groupby(['trend']).size()
            series_to_dict = series.to_dict()

            board = another_board['board']
            for trend in ['up', 'down', 'enlarge', 'convergence']:
                if trend in series_to_dict.keys():
                    size = series_to_dict[trend]
                    result_list.append(
                        dict(industry=board, trend=trend, size=size, rate=round(size / len(total), 2),
                             date=date,
                             update=datetime.now()))
                else:
                    result_list.append(
                        dict(industry=board, trend=trend, size=0, rate=0, date=date,
                             update=datetime.now()))

    for date in WorkDayIterator(start, end):
        print(date)
        trend_point_set = db['trend_point']
        r = list(trend_point_set.find(
            {"date": {"$lte": date},
             "update": {"$gte": date}}))
        if len(r) == 0: continue
        df = pd.DataFrame(r)
        series = df.groupby(['industry', 'trend']).size()
        series_to_dict = series.to_dict()

        for item in boards:
            board = item['board']
            for trend in ['up', 'down', 'enlarge', 'convergence']:
                if (board, trend) in series_to_dict.keys():
                    size = series_to_dict[(board, trend)]
                    result_list.append(
                        dict(industry=board, trend=trend, size=size, rate=round(size / board_dict[board], 2), date=date,
                             update=datetime.now()))
                else:
                    result_list.append(
                        dict(industry=board, trend=trend, size=0, rate=0, date=date,
                             update=datetime.now()))


        # collected_industry = []
        # for  k,v in series_to_dict.items():
        #     result_list.append(dict(industry=k[0], trend=k[1], size=v, rate=round(v / board_dict[k[0]], 2), date=date,
        #          update=datetime.now()))
        #     collected_industry.append(k[0])

        # result_list = [dict(industry=k[0], trend=k[1], size=v, rate=round(v / board_dict[k[0]], 2), date=date,
        #                     update=datetime.now()) for k, v
        #                in series_to_dict.items()]

        # 补全没有出现的数据

    for result in result_list:
        print("insert {},{},{}".format(result["industry"],result["trend"],result['date']))
        db.trend_data.update_one(
            {"industry": result["industry"], "trend": result["trend"],
             "date": result['date']}, {"$set": result}, upsert=True)


if __name__ == "__main__":
    for date in WorkDayIterator(datetime(2022, 7, 5), datetime(2022, 8, 25)):
        features = stock_dao.get_company_feature("300763", date)
        save_stock_trend_with_features("300763", "锦浪科技", features, date)

    # save_stock_trend_with_features("300763", "锦浪科技", features, datetime(2022, 8, 25))
    # get_trend_size_info(datetime(2022, 4, 1), datetime(2022, 8, 24))

    # print("code","300763")
