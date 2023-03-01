"""
趋势相关服务
"""
import logging
import logging as log
from collections import OrderedDict
from datetime import datetime, timedelta

import pandas as pd
from pymongo.errors import AutoReconnect
from retrying import retry

from app.main.db.mongo import db
from app.main.stock import constant
from app.main.stock.company import Company
from app.main.stock.dao import stock_dao, board_dao, k_line_dao
from app.main.stock.service import board_service
from app.main.utils import date_util, cal_util, stock_util
from app.main.utils.date_util import WorkDayIterator

normal = 1
frozen = 2
temp = 3


def get_trend_data(date, industries):
    return list(db['trend_data'].find({"date": date, "industry": {"$in": industries}}))


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

        in_trade_time = start_of_day == date_util.get_start_of_day(datetime.now()) \
                        and date_util.in_trade_time(datetime.now())

        if not in_trade_time:
            trend_point_set.delete_many({"code": code, "trend_type": frozen})
            trend_point_set.update_many({"code": code, "trend_type": temp},
                                        {"$set": {"trend_type": normal, "is_in_use": 1}})

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

        # 顶分型趋势
        # 底分型趋势
        # 任何趋势变化,就新增一条记录
        trend_change_scope = []
        # 获取最近一个趋势状态
        trend_point_list = list(trend_point_set.find({"code": code, "is_deleted": 0,
                                                      "date": {"$lte": start_of_day}},
                                                     sort=[("date", -1), ("_id", -1)]).limit(2))
        trend_point = None
        # 历史记录不为空,就要做更新
        if len(trend_point_list) > 0:
            trend_point = trend_point_list[0]
            inf_l_point_date_history = trend_point['inf_l_point_date']  # 底分型拐点出现的时间
            inf_h_point_date_history = trend_point['inf_h_point_date']  # 顶分型拐点出现的时间
            prev_inf_l_point_date = trend_point['prev_inf_l_point_date']
            prev_inf_h_point_date = trend_point['prev_inf_h_point_date']

            # 判断时间区间
            # 如果是日内的话，且有变更，不对原来的数据内容做变更,临时拷贝一条记录插入，并将最近一条记录更新为特殊状态
            # 如果在日内的

            # inf_l_point_date 和 inf_h_point_date 这个拐点数据，随着日内随时会出现波动
            # 和之前都不一致
            if inf_l_point_date_history != inf_l_point_date \
                    and prev_inf_l_point_date != inf_l_point_date:
                trend_change_scope.append(1)
            if inf_h_point_date_history != inf_h_point_date \
                    and prev_inf_h_point_date != inf_h_point_date:
                trend_change_scope.append(2)

            # 日内波动引起的改动,直接将该记录软删除
            # if inf_h_point_date == prev_inf_h_point_date or inf_l_point_date == prev_inf_l_point_date:
            #     trend_point_set.update_one({"_id": trend_point["_id"]}, {"$set": {"is_deleted":1}})
            #     return

        # 没有任何变化,更新，只要有变化，就新增一条记录
        if len(trend_change_scope) == 0 and trend_point:
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

        # 在交易时间的，状态设置为临时
        trend_type = temp if in_trade_time else normal

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
            prev_trend=trend_point['trend'] if trend_point else None,  # 之前总体趋势
            inf_l_point_date=inf_l_point_date,  # 底分型趋势成立时间
            inf_h_point_date=inf_h_point_date,  # 顶分型趋势成立时间
            prev_inf_l_point_date=trend_point['inf_l_point_date'] if trend_point else None,
            prev_inf_h_point_date=trend_point['inf_h_point_date'] if trend_point else None,
            trend_change_scope=trend_change_scope,  # 趋势变化记录
            industry=stock_detail['industry'],  # 行业
            name=name,
            code=code,
            update=start_of_day,
            update_time=datetime.now(),
            inf_l_point_value=inf_l_point_value,
            inf_h_point_value=inf_h_point_value,
            is_deleted=0,
            trend_type=trend_type
        )
        trend_point_set.save(entity)
        if (trend_point):
            update_item = {"is_in_use": 0}
            if in_trade_time:
                update_item['trend_type'] = frozen

            trend_point_set.update_one({"_id": trend_point["_id"]}, {"$set": update_item})
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


def _retry_if_auto_reconnect_error(exception):
    """Return True if we should retry (in this case when it's an AutoReconnect), False otherwise"""
    return isinstance(exception, AutoReconnect)


@retry(retry_on_exception=_retry_if_auto_reconnect_error, stop_max_attempt_number=2, wait_fixed=2000)
def _get_trend_point(date):
    trend_point_set = db['trend_point']
    r = list(trend_point_set.find(
        {"date": {"$lte": date},
         "update": {"$gte": date}}))
    return r


def get_province_trend_info(start, end):
    """
    获取省份的涨跌趋势
    :param start:
    :param end:
    :return:
    """
    code_province_dict = stock_dao.get_code_province_map()
    for date in WorkDayIterator(start, end):

        r = _get_trend_point(date)
        if len(r) == 0: continue
        df = pd.DataFrame(r)
        df['province'] = df.apply(lambda row: code_province_dict.get(row['code']), axis=1)
        grouped = df.groupby(['province', 'trend'])
        series_to_dict = grouped.size().to_dict()
        series_province = df.groupby(['province']).size()
        result_list = []

        for province in series_province.to_dict().keys():
            for trend in ['up', 'down', 'enlarge', 'convergence']:
                if (province, trend) in series_to_dict.keys():
                    size = series_to_dict[(province, trend)]
                    result_list.append(
                        dict(industry=province, trend=trend, size=size,
                             rate=cal_util.round(size / int(series_province[province]), 4),
                             date=date,
                             total=int(series_province[province]),
                             update=datetime.now(),
                             type="province"))
                else:
                    result_list.append(
                        dict(industry=province, trend=trend, size=0, rate=0, total=0, date=date,
                             update=datetime.now(),
                             type="province"))

        for result in result_list:
            print("insert {},{},{}".format(result["industry"], result["trend"], result['date']))
            db.trend_data.update_one(
                {"industry": result["industry"], "trend": result["trend"],
                 "date": result['date']}, {"$set": result}, upsert=True)

def get_index_trend_info(start, end):
    """
    获取大盘的趋势分组数据
    :param start:
    :param end:
    :return:
    """
    for date in WorkDayIterator(start, end):
        r = _get_trend_point(date)
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
                             rate=cal_util.round(size / int(series_market[market]), 4),
                             date=date,
                             total=int(series_market[market]),
                             update=datetime.now(),
                             type="market"))
                else:
                    result_list.append(
                        dict(industry=market, trend=trend, size=0, rate=0, total=0, date=date,
                             update=datetime.now(),
                             type="market"))

        for result in result_list:
            print("insert {},{},{}".format(result["industry"], result["trend"], result['date']))
            db.trend_data.update_one(
                {"industry": result["industry"], "trend": result["trend"],
                 "date": result['date']}, {"$set": result}, upsert=True)


def get_trend_info_by_name(board_name, start, end):
    """
    特定板块跑数据
    :param board:
    :param start:
    :param end:
    :return:
    """
    board = board_dao.get_board_by_name(board_name)
    result_list = []

    for date in WorkDayIterator(start, end):
        logging.info("完成对{}板块的趋势分析:{}".format(board_name, date))
        trend_point_set = db['trend_point']
        total = board['codes']
        r = list(trend_point_set.find(
            {"date": {"$lte": date},
             "update": {"$gte": date}, "code": {"$in": total}, "trend_type": {"$in": [normal, temp]}}))
        if len(r) == 0: continue
        df = pd.DataFrame(r)
        series = df.groupby(['trend']).size()
        series_to_dict = series.to_dict()

        for trend in ['up', 'down', 'enlarge', 'convergence']:
            if trend in series_to_dict.keys():
                size = series_to_dict[trend]
                result_list.append(
                    dict(industry=board_name, trend=trend, size=size, rate=cal_util.round(size / len(total), 4),
                         total=len(total),
                         date=date,
                         update=datetime.now()))
            else:
                result_list.append(
                    dict(industry=board, trend=trend, size=0, rate=0,
                         total=len(total),
                         date=date,
                         update=datetime.now()))

        lines = k_line_dao.get_k_line_data(date, date, codes=total)
        money_sum = sum([line['money'] for line in lines])
        volume_sum = sum([line['volume'] for line in lines])
        money = cal_util.divide(money_sum, 100000000, 3)
        logging.info("同步板块{}的交易量和成交额:{},{},{}".format(board_name, date, money, volume_sum))
        update_item = dict(industry=board_name, date=date,
                           volume=volume_sum, money=money)
        db['board_trade_volume'].update_one({"industry": board_name, "date": date},
                                            {"$set": update_item}, upsert=True)

    _dump_trend_data(result_list)


def get_board_trend_size_info(start, end, only_include=False):
    """
    获取各个板块的趋势分组数据
    :return:
    """
    board_detail = db['board_detail']
    boards = list(board_detail.find({"type": 2}))
    board_dict = {board['board']: board['size'] for board in boards}

    result_list = []

    # 自定义的板块跑批
    config = db['config']
    board_info = config.find_one({"name": "board"}, {"_id": 0})
    another_boards = board_info['value']

    another_boards = list(board_detail.find({"board": {"$in": another_boards}}))

    for date in WorkDayIterator(start, end):
        for another_board in another_boards:
            trend_point_set = db['trend_point']
            total = another_board['codes']
            r = list(trend_point_set.find(
                {"date": {"$lte": date},
                 "update": {"$gte": date}, "code": {"$in": total}, "trend_type": {"$in": [normal, temp]}}))
            if len(r) == 0: continue
            df = pd.DataFrame(r)
            series = df.groupby(['trend']).size()
            series_to_dict = series.to_dict()

            board = another_board['board']
            for trend in ['up', 'down', 'enlarge', 'convergence']:
                if trend in series_to_dict.keys():
                    size = series_to_dict[trend]
                    result_list.append(
                        dict(industry=board, trend=trend, size=size, rate=cal_util.round(size / len(total), 4),
                             total=len(total),
                             date=date,
                             update=datetime.now(),
                             type="custom"))
                else:
                    result_list.append(
                        dict(industry=board, trend=trend, size=0, rate=0,
                             total=len(total),
                             date=date,
                             update=datetime.now(),
                             type="custom"))

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
                                 rate=cal_util.round(size / board_dict[board], 4),
                                 total=board_dict[board],
                                 date=date,
                                 update=datetime.now(),
                                 type="industry"))
                    else:
                        result_list.append(
                            dict(industry=board, trend=trend, size=0, rate=0,
                                 total=board_dict[board],
                                 date=date, bot=0, top=0,
                                 update=datetime.now(),
                                 type="industry"))

    for result in result_list:
        industry = result["industry"]
        trend = result["trend"]
        print("insert {},{},{}".format(result["industry"], result["trend"], result['date']))

        range_end = result['date']
        range_start = range_end - timedelta(60)
        # 写入当前趋势
        trend_data_list = list(db.trend_data.find({"industry": industry, 'trend': trend,
                                                   "date": {"$gte": range_start, "$lte": range_end},
                                                   }).sort("date", 1))
        trend_data_rate = [point['rate'] for point in trend_data_list]

        if len(trend_data_rate) > 0:
            trend_data_rate[len(trend_data_rate) - 1] = result['rate']
        else:
            trend_data_rate.append(result['rate'])

        high_type_list: list = cal_util.get_top_type(trend_data_rate)
        low_type_list: list = cal_util.get_bottom_type(trend_data_rate)

        pos_p, neg_p, total_p, point_index = cal_util.get_reverse_point(high_type_list)
        if len(total_p) == 0:
            current_trend_scope = high_type_list
        else:
            current_trend_scope = high_type_list[total_p[-1]:]

        current_trend_scope = [item for item in current_trend_scope if item['index'] != len(trend_data_list) - 1]
        max_top_type = 0 if len(current_trend_scope) == 0 else current_trend_scope[len(current_trend_scope) - 1][
            'value']

        pos_p, neg_p, total_p, point_index = cal_util.get_reverse_point(low_type_list)
        if len(total_p) == 0:
            current_trend_scope = low_type_list
        else:
            current_trend_scope = low_type_list[total_p[-1]:]

        current_trend_scope = [item for item in current_trend_scope if item['index'] != len(trend_data_list) - 1]
        max_bot_type = 0 if len(current_trend_scope) == 0 else current_trend_scope[len(current_trend_scope) - 1][
            'value']
        x, c = cal_util.get_line([max_top_type, result['rate']])
        result['up_slop'] = x
        x, c = cal_util.get_line([max_bot_type, result['rate']])
        result['down_slop'] = x

        db.trend_data.update_one(
            {"industry": result["industry"], "trend": result["trend"],
             "date": result['date']}, {"$set": result}, upsert=True)


def get_trend_info(end_date):
    """
    趋势信息列表展示
    :param end_date:
    :return:
    """
    # config = db['config']
    # boards = config.find_one({"name": "board"}, {"_id": 0})
    industries = board_service.get_all_board_names()

    trend_data = db['trend_data']
    end = date_util.get_latest_work_day() if end_date is None else end_date
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
        enlarge = df[(df['industry'] == industry) & (df['trend'] == 'enlarge')].reset_index(drop=True)
        convergence = df[(df['industry'] == industry) & (df['trend'] == 'convergence')].reset_index(drop=True)

        rate_diff = down['rate'] - up['rate']
        up['diff'] = rate_diff
        latest = rate_diff[0]
        result = _analysis(up, down,enlarge,convergence)
        result['name'] = industry
        # total[industry] = round(latest,2)
        total.append(result)
    total = sorted(total, key=lambda item: item['currentDiff'], reverse=True)

    df = pd.DataFrame(total)
    labels = ["-1~-0.75", "-0.75~-0.5", "-0.5~-0.25",
              "-0.25~0", "0~0.25", "0.25~0.5",
              "0.5~0.75", "0.75~1"]
    df['cut'] = pd.cut(df.currentDiff, bins=[-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1],
                       labels=labels,
                       include_lowest=True)
    industry_info = OrderedDict()
    for label in labels:
        items = list(df[df['cut'] == label]['name'])
        industry_info[label] = dict(industries=items, rate=cal_util.round(len(items) / len(industries), 2))

    return dict(records=df.to_dict("records"),
                industryInfo=industry_info)


def _dump_trend_data(result_list):
    for result in result_list:
        industry = result["industry"]
        trend = result["trend"]
        print("insert {},{},{}".format(result["industry"], result["trend"], result['date']))

        range_end = result['date']
        range_start = range_end - timedelta(60)
        # 写入当前趋势
        trend_data_list = list(db.trend_data.find({"industry": industry, 'trend': trend,
                                                   "date": {"$gte": range_start, "$lte": range_end},
                                                   }).sort("date", 1))
        trend_data_rate = [point['rate'] for point in trend_data_list]

        if len(trend_data_rate) > 0:
            trend_data_rate[len(trend_data_rate) - 1] = result['rate']
        else:
            trend_data_rate.append(result['rate'])

        high_type_list: list = cal_util.get_top_type(trend_data_rate)
        low_type_list: list = cal_util.get_bottom_type(trend_data_rate)

        pos_p, neg_p, total_p, point_index = cal_util.get_reverse_point(high_type_list)
        if len(total_p) == 0:
            current_trend_scope = high_type_list
        else:
            current_trend_scope = high_type_list[total_p[-1]:]

        current_trend_scope = [item for item in current_trend_scope if item['index'] != len(trend_data_list) - 1]
        max_top_type = 0 if len(current_trend_scope) == 0 else current_trend_scope[len(current_trend_scope) - 1][
            'value']

        pos_p, neg_p, total_p, point_index = cal_util.get_reverse_point(low_type_list)
        if len(total_p) == 0:
            current_trend_scope = low_type_list
        else:
            current_trend_scope = low_type_list[total_p[-1]:]

        current_trend_scope = [item for item in current_trend_scope if item['index'] != len(trend_data_list) - 1]
        max_bot_type = 0 if len(current_trend_scope) == 0 else current_trend_scope[len(current_trend_scope) - 1][
            'value']
        x, c = cal_util.get_line([max_top_type, result['rate']])
        result['up_slop'] = x
        x, c = cal_util.get_line([max_bot_type, result['rate']])
        result['down_slop'] = x

        db.trend_data.update_one(
            {"industry": result["industry"], "trend": result["trend"],
             "date": result['date']}, {"$set": result}, upsert=True)


def _analysis(up_df, down_df,enlarge_df,convergence_df):
    # 最低上行率
    lowest_up = up_df.iloc[[up_df['rate'].idxmin()]]
    # 历史最高上行率
    highest_up = up_df.iloc[[up_df['rate'].idxmax()]]
    # 区间差距最大的一天,和值
    max_diff = up_df.iloc[[up_df['diff'].idxmax()]]
    # 当前区间差距
    current_diff = up_df.iloc[[len(up_df) - 1]]
    current_down = down_df.iloc[[len(down_df) - 1]]
    current_convergence = convergence_df.iloc[len(convergence_df)-1]
    current_enlarge = enlarge_df.iloc[len(enlarge_df)-1]
    result = dict(
        # lowestUpDay=lowest_up.iloc[0]['date'].strftime('%Y-%m-%d'),
        # highestUpDay=lowest_up.iloc[0]['date'].strftime('%Y-%m-%d'),
        # maxDiffDay=lowest_up.iloc[0]['date'].strftime('%Y-%m-%d'),
        lowestUpValue=cal_util.round(lowest_up['rate']),
        highestUp=cal_util.round(highest_up['rate']),
        maxDiffValue=cal_util.round(max_diff['diff']),
        currentDiff=cal_util.round(current_diff['diff']),
        currentUpValue=cal_util.round(current_diff['rate']),
        currentDownValue=cal_util.round(current_down['rate']),
        currentConvergenceValue=cal_util.round(current_convergence['rate']),
        currentEnlargeValue=cal_util.round(current_enlarge['rate']),
        up_slop=cal_util.round(current_diff['up_slop']),
        down_slop=cal_util.round(current_diff['down_slop']),
        convergence_down_slop=cal_util.round(current_convergence['down_slop']),
        convergence_up_slop=cal_util.round(current_convergence['up_slop']),
        enlarge_down_slop=cal_util.round(current_enlarge['down_slop']),
        enlarge_up_slop=cal_util.round(current_enlarge['up_slop']),
    )
    return result


if __name__ == "__main__":
    # r = list(db['trend_point'].find(
    #     {"industry": "电网设备", "date": {"$lte": datetime(2023,2,15)}, "update": {"$gte": datetime(2023,2,15)}}))
    #
    # codes = [i['code'] for i in r]
    #
    # codes2 = db['board_detail'].find_one({"board":"电网设备"})['codes']
    # diff = set(codes2).difference(set(codes))
    # print(123)

    # from_date = date_util.get_start_of_day(date_util.from_timestamp(int(1665331200000)))
    #
    # end_date = date_util.get_start_of_day(date_util.from_timestamp(int(1665331200000)))
    # log.info("get_trend_data_task {},{}:{}".format("14a3c4d8-48b4-11ed-bb4c-00163e0a10b2", from_date, end_date))
    #
    # # 板块级别的聚合
    # get_trend_size_info(from_date, end_date)
    # # 大盘级别的聚合
    # get_all_trend_info(from_date, end_date)
    # stocks = stock_dao.get_all_stock()
    # for stock in stocks:
    #     code = stock['code']
    #     name = stock['name']
    #     print(code, name)
    #
    #     for date in WorkDayIterator(datetime(2022, 10, 26), datetime(2022, 10, 26)):
    #         features = stock_dao.get_company_feature(code, date)
    #         save_stock_trend_with_features(code, name, features, date)

    # save_stock_trend_with_features("300763", "锦浪科技", features, datetime(2022, 8, 25))
    # get_trend_size_info(datetime(2022, 9, 16), datetime(2022, 9, 16), False)
    # get_all_trend_info(datetime(2022, 4, 1), datetime(2022, 9, 16))
    # print("code","300763")
    # get_trend_info_by_name('中字头',datetime(2019, 1, 1), datetime(2022, 12, 5))

    get_trend_info(datetime(2023, 2, 17))

    # from_date = datetime(2021, 1, 1)
    # end_date = datetime(2023, 2, 20)
    # # 板块级别的聚合
    # get_board_trend_size_info(from_date, end_date)
    # # 大盘级别的聚合
    # get_index_trend_info(from_date, end_date)
    # # 省份级别的聚合
    # get_province_trend_info(from_date, end_date)
    # # 板块，大盘，省份的成交量和成交额的聚合
    # board_service.collect_trade_money(from_date, end_date)
