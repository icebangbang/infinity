"""
趋势相关服务
"""
from collections import OrderedDict

from app.main.db.mongo import db
from app.main.stock import constant
from app.main.stock.company import Company
from app.main.stock.const import board_const
from app.main.stock.dao import stock_dao
from datetime import datetime
import pandas as pd

from app.main.stock.service import board_service
from app.main.utils import date_util, cal_util, stock_util
from app.main.utils.date_util import WorkDayIterator
import logging as log


def save_stock_trend_with_features(code, name, features, start_of_day: datetime):
    """
    从特征中提取趋势数据,并保存
    :param code:
    :param name:
    :param features:
    :param start_of_day:
    :return:
    """
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


def get_all_trend_info(start, end):
    """
    获取大盘的趋势分组数据
    :param start:
    :param end:
    :return:
    """
    for date in WorkDayIterator(start, end):
        print(date)
        trend_point_set = db['trend_point']
        r = list(trend_point_set.find(
            {"date": {"$lte": date},
             "update": {"$gte": date}}))
        if len(r) == 0: continue
        df = pd.DataFrame(r)
        df['market'] = df.apply(lambda row: stock_util.market_belong(row['code']), axis=1)
        series = df.groupby(['market', 'trend']).size()
        series_to_dict = series.to_dict()
        series_market = df.groupby(['market']).size()

        result_list = []
        for market in ['沪市', '深市', '科创板', '创业板']:
            for trend in ['up', 'down', 'enlarge', 'convergence']:
                if (market, trend) in series_to_dict.keys():
                    size = series_to_dict[(market, trend)]
                    result_list.append(
                        dict(industry=market, trend=trend, size=size,
                             rate=cal_util.round(size / int(series_market[market]), 2),
                             date=date,
                             update=datetime.now()))
                else:
                    result_list.append(
                        dict(industry=market, trend=trend, size=0, rate=0, date=date,
                             update=datetime.now()))

        for result in result_list:
            print("insert {},{},{}".format(result["industry"], result["trend"], result['date']))
            db.trend_data.update_one(
                {"industry": result["industry"], "trend": result["trend"],
                 "date": result['date']}, {"$set": result}, upsert=True)


def get_trend_size_info(start, end, only_include=False):
    """
    获取各个板块的趋势分组数据
    :return:
    """
    board_detail = db['board_detail']
    boards = list(board_detail.find({"type": 2}))
    board_dict = {board['board']: board['size'] for board in boards}

    result_list = []

    config = db['config']
    board_info = config.find_one({"name": "board"}, {"_id": 0})
    another_boards = board_info['value']

    another_boards = list(board_detail.find({"board": {"$in": another_boards}}))

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
                        dict(industry=board, trend=trend, size=size, rate=cal_util.round(size / len(total), 2),
                             date=date,
                             update=datetime.now()))
                else:
                    result_list.append(
                        dict(industry=board, trend=trend, size=0, rate=0, date=date,
                             update=datetime.now()))
    if not only_include:
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
                            dict(industry=board, trend=trend, size=size,
                                 rate=cal_util.round(size / board_dict[board], 2),
                                 date=date,
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
        print("insert {},{},{}".format(result["industry"], result["trend"], result['date']))
        db.trend_data.update_one(
            {"industry": result["industry"], "trend": result["trend"],
             "date": result['date']}, {"$set": result}, upsert=True)


def get_trend_info():
    # config = db['config']
    # boards = config.find_one({"name": "board"}, {"_id": 0})
    industries = board_service.get_all_board()

    trend_data = db['trend_data']
    end = date_util.get_latest_work_day()
    start = date_util.get_work_day(end, 120)
    trend_data_list = list(trend_data.find({"industry": {"$in": industries},
                                            "date": {"$gte": start, "$lte": end},
                                            }))
    total = []
    df = pd.DataFrame(trend_data_list)
    df.sort_values("date", ascending=True, inplace=True)
    for industry in industries:
        up = df[(df['industry'] == industry) & (df['trend'] == 'up')].reset_index(drop=True)
        down = df[(df['industry'] == industry) & (df['trend'] == 'down')].reset_index(drop=True)

        rate_diff = down['rate'] - up['rate']
        up['diff'] = rate_diff
        latest = rate_diff[0]
        result = _analysis(up, down)
        result['name'] = industry
        # total[industry] = round(latest,2)
        total.append(result)
    total = sorted(total, key=lambda item: item['currentDiff'], reverse=True)

    df = pd.DataFrame(total)
    labels = ["0-0.1", "0.1-0.2", "0.2-0.3",
              "0.3-0.4", "0.4-0.5", "0.5-0.6",
              "0.6-0.7", "0.7-0.8", "0.8-0.9", "0.9-1"]
    df['cut'] = pd.cut(df.currentUpValue, bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
                       labels=labels,
                       include_lowest=True)
    industry_info = OrderedDict()
    for label in labels:
        items = list(df[df['cut'] == label]['name'])
        industry_info[label] = dict(industries=industries, rate=cal_util.round(len(items) / len(industries), 2))

    return dict(records=df.to_dict("records"),
                industryInfo=industry_info)


def _analysis(up_df, down_df):
    # 最低上行率
    lowest_up = up_df.iloc[[up_df['rate'].idxmin()]]
    # 历史最高上行率
    highest_up = up_df.iloc[[up_df['rate'].idxmax()]]
    # 区间差距最大的一天,和值
    max_diff = up_df.iloc[[up_df['diff'].idxmax()]]
    # 当前区间差距
    current_diff = up_df.iloc[[len(up_df) - 1]]
    current_down = down_df.iloc[[len(down_df) - 1]]
    result = dict(
        lowestUpValue=cal_util.round(lowest_up['rate']),
        lowestUpDay=lowest_up.iloc[0]['date'].strftime('%Y-%m-%d'),
        highestUp=cal_util.round(highest_up['rate']),
        highestUpDay=lowest_up.iloc[0]['date'].strftime('%Y-%m-%d'),
        maxDiffValue=cal_util.round(max_diff['diff']),
        maxDiffDay=lowest_up.iloc[0]['date'].strftime('%Y-%m-%d'),
        currentDiff=cal_util.round(current_diff['diff']),
        currentUpValue=cal_util.round(current_diff['rate']),
        currentDownValue=cal_util.round(current_down['rate']),

    )
    return result


if __name__ == "__main__":
    for date in WorkDayIterator(datetime(2022, 4, 1), datetime(2022, 8, 29)):
        get_all_trend_info(date, date)
    #     features = stock_dao.get_company_feature("300763", date)
    #     save_stock_trend_with_features("300763", "锦浪科技", features, date)

    # save_stock_trend_with_features("300763", "锦浪科技", features, datetime(2022, 8, 25))
    # get_trend_size_info(datetime(2022, 4, 1), datetime(2022, 8, 26), True)

    # print("code","300763")
