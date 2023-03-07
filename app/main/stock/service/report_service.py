from datetime import datetime, timedelta

from app.main.utils import date_util
from app.main.stock.dao import stock_dao, k_line_dao
from collections import OrderedDict
import dateutil
from app.main.db.mongo import db
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from app.main.stock.dao import k_line_dao, stock_dao
from app.main.utils import date_util
import numpy
from app.main.db.mongo import db
import pandas as pd
from app.main.utils import cal_util
import numpy as np


def get_overview():
    now = datetime.now()
    # 目前同步的k线的最早时间
    point = k_line_dao.get_earliest_k_line()
    # 库内最早k线日期字段判空
    date = date_util.dt_to_str(point['date'], '%Y-%m-%d') if point else "暂无数据"
    # k线数据创建时间字段判空
    create_time = date_util.dt_to_str(point['create_time'], '%Y-%m-%d %H:%M:%S') if point else "暂无数据"

    # 特征跑批时间
    feature_point = stock_dao.get_latest_stock_feature()
    feature_update_time = date_util.dt_to_str(feature_point['update_time'], '%Y-%m-%d %H:%M:%S') \
        if feature_point else "暂无数据"

    # 获取当前节气数据
    jq_list = date_util.get_jq_list(now, now + timedelta(30))
    current_jq = jq_list[0]
    next_jq = jq_list[1]
    # 获取下一个节气的数据
    day_until_next_jq = date_util.get_days_between(next_jq['time'], now)

    # 获取年月日时干支
    date_gz = date_util.get_date_gz(now)

    return dict(earliest_kline_day=date,
                kline_day_latest_update=create_time,
                feature_latest_update=feature_update_time,
                current_jq=current_jq['jq'],
                next_jq=next_jq['jq'],
                day_until_next_jq=day_until_next_jq,
                date_gz=date_gz)


def rps_analysis(date=None, offset=-250):
    """
    个股强弱排名
    :param date:
    :return:
    """
    end = datetime.now() if date is None else date
    rate_250_list = []

    if date_util.is_workday(end) is False or date_util.is_weekend(end):
        return

    stocks = stock_dao.get_all_stock(fields=dict(code=1, name=1, _id=0))
    for index, stock in enumerate(stocks):
        code = stock['code']
        name = stock['name']
        # logging.info("{},{}".format(index, code))

        data_list = k_line_dao.get_k_line_data_by_offset(end, offset, code=code)
        if len(data_list) >= abs(offset):
            k_start_prev = data_list[0]['prev_close'] if data_list[0]['prev_close'] != 0 else data_list[0]['close']
            k_end_close = data_list[len(data_list) - 1]['close']
            rate = cal_util.get_rate(k_end_close - k_start_prev, k_start_prev)
            rate_250_list.append(dict(code=code, rate=rate, name=name))

    results = sorted(rate_250_list, key=lambda x: x['rate'], reverse=True)
    split_100_list = np.array_split(results, 100)
    results = []
    for index, groups in enumerate(split_100_list):
        for sub_index, item in enumerate(groups):
            item['rps'] = 100 - index - cal_util.round(1 / len(groups) * sub_index, 2)
            item['date'] = date_util.get_start_of_day(end)
            item['span'] = abs(offset)
            results.append(item)
    for result in results:
        db['rps_anslysis'].update({"code": result['code'], 'date': result['date'], "span": abs(offset)},
                                  {"$set": result}, upsert=True)


def up_down_limit_analysis(date):
    """
    这跌停情况分析
    :return:
    """
    date = datetime.now() if date is None else date
    start = date_util.get_start_of_day(date)
    stock_feature = db['stock_feature']
    results = list(stock_feature.find({"features.cont_up_limit_count": {"$gte": 1},
                                       "date": start}))

    stocks = [dict(name=result['name'],
                   cont_up_limit_count=result['features']['cont_up_limit_count']) for result in results]
    df = pd.DataFrame(stocks)
    df['cut'] = pd.cut(df.cont_up_limit_count, bins=[0, 1, 2, 3, 4, 5, 100], labels=["1", "2", "3", "4", "5", ">=6"],
                       include_lowest=False)

    group_result = {cut: [r['name'] for r in group.to_dict('records')] for cut, group in df.groupby('cut')}
    #     total = list(set.find({"date": {"$lte": date, "$gte": date - timedelta(days=1)}, "type": board_type}))


def baotuan_analysis():
    """
    包团分析
    :return:
    """
    start_time = datetime(2019, 1, 1)
    end_time = date_util.get_start_of_day(datetime.now())
    storage = []
    while (start_time < end_time):
        base = start_time
        next = start_time + dateutil.relativedelta.relativedelta(months=1)
        next_before = next - timedelta(days=1)

        data_list = k_line_dao.get_k_line_data(base, next_before, level='month')
        if len(data_list) == 0:
            start_time = next
            continue
        group = {}
        for data in data_list:
            code = data['code']
            line_list = group.get(code, [])
            line_list.append(data)
            group[code] = line_list

        total_money = 0
        money_group = {}
        for k, stock_data_list in group.items():
            stock_money = sum(v['money'] for v in stock_data_list)
            total_money = total_money + stock_money
            money_group[k] = stock_money

        sorted_values = sorted(money_group.values(), reverse=True)
        top_5 = sorted_values[0:int(len(sorted_values) * 0.05)]
        percent = round(sum(top_5) / total_money, 3)
        storage.append(dict(date=start_time, percent=percent, update=datetime.now()))
        logging.info("[baotuan analysis] start month:{}:".format(date_util.dt_to_str(start_time), percent))
        start_time = next
    set = db['baotuan_analysis']
    set.drop()
    set.insert_many(storage)


def market_status_analysis(date=None):
    """
    涨跌情况分析
    :return:
    """
    date = datetime.now() if date is None else date
    if date_util.is_workday(date) is False: return
    if date.hour >= 15 or date.hour <= 8: return
    if date > datetime(date.year, date.month, date.day, 11, 30, 00) and \
            date < datetime(date.year, date.month, date.day, 13, 00, 00):
        return

    now = date_util.get_start_of_day(date)
    stocks = stock_dao.get_all_stock(dict(code=1, name=1, _id=0))
    st_stock = {stock['code']: stock['name'] for stock in stocks if "ST" in stock['name']}
    stock_dict = {stock['code']: stock['name'] for stock in stocks}
    # start, end = date_util.get_work_day(now, 1)
    trade_data_list = k_line_dao.get_k_line_data(now, now)
    groups = {trade_data['code']: trade_data for trade_data in trade_data_list}
    # for trade_data in trade_data_list:
    #     code = trade_data['code']
    #     items = groups.get(code)
    #     items.append(trade_data)
    #     groups[code] = items
    rate_list = []

    up_down_distribution = {"跌停": 0, "跌停~8%": 0, "-8%~-6%": 0, "-6%~-4%": 0, "-4%~-2%": 0, "-2%~0%": 0,
                            "0%~2%": 0, "2%~4%": 0,
                            "4%~6%": 0, "6%~8%": 0, "8%~涨停": 0, "涨停": 0}
    limit_up_stock = []
    limit_down_stock = []

    for key, trade_data in groups.items():
        # close_1 = trade_data_list[0]['close']
        # close_2 = trade_data_list[1]['close']
        code = trade_data['code']
        close_2 = trade_data['close']
        close_1 = trade_data['prev_close']
        rate = Decimal((close_2 - close_1) / close_1 * 100).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
        rate_list.append(rate)

        if key.startswith("3") or key.startswith("68"):
            if Decimal(close_1 * 1.2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                # 20cm
                up_down_distribution['涨停'] = up_down_distribution['涨停'] + 1
                limit_up_stock.append(
                    dict(name=stock_dict[code], type='cyb' if key.startswith("3") else 'kcb'))
                continue
        else:
            if key in st_stock.keys() and Decimal(close_1 * 1.05).quantize(Decimal("0.01"),
                                                                           rounding="ROUND_HALF_UP").compare(
                Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                up_down_distribution['涨停'] = up_down_distribution['涨停'] + 1
                limit_up_stock.append(
                    dict(name=stock_dict[code], type='sh' if key.startswith("60") else 'sz'))
                continue
            elif Decimal(close_1 * 1.1).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                up_down_distribution['涨停'] = up_down_distribution['涨停'] + 1
                limit_up_stock.append(
                    dict(name=stock_dict[code], type='sz' if key.startswith("00") else 'sh'))
                continue

        if key.startswith("3") or key.startswith("688"):
            if Decimal(close_1 * 0.8).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                # 20cm
                up_down_distribution['跌停'] = up_down_distribution['跌停'] + 1
                limit_down_stock.append(
                    dict(name=stock_dict[code], rate=float(rate), type='cyb' if key.startswith("3") else 'kcb'))
                continue
        else:
            if key in st_stock.keys() and Decimal(close_1 * 0.95).quantize(Decimal("0.01"),
                                                                           rounding="ROUND_HALF_UP").compare(
                Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                up_down_distribution['跌停'] = up_down_distribution['跌停'] + 1
                limit_down_stock.append(
                    dict(name=stock_dict[code], type='sh' if key.startswith("60") else 'sz'))
                continue
            elif Decimal(close_1 * 0.9).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                up_down_distribution['跌停'] = up_down_distribution['跌停'] + 1
                limit_down_stock.append(
                    dict(name=stock_dict[code], type='sh' if key.startswith("60") else 'sz'))
                continue

        # "跌停~8%": 0, "-8%~-6%": 0, "-6%~-4%": 0, "-4%~-2%": 0, "-2%~0%": 0,
        #                             "0%~2%": 0, "2%~4%": 0,
        #                             "4%~6%": 0, "6%~8%": 0, "8%~涨停": 0, "涨停": 0

        if rate < -8:
            up_down_distribution['跌停~8%'] = up_down_distribution['跌停~8%'] + 1
            continue
        if -8 <= rate < -6:
            up_down_distribution['-8%~-6%'] = up_down_distribution['-8%~-6%'] + 1
            continue
        if -6 <= rate < -4:
            up_down_distribution['-6%~-4%'] = up_down_distribution['-6%~-4%'] + 1
            continue
        if -4 <= rate < -2:
            up_down_distribution['-4%~-2%'] = up_down_distribution['-4%~-2%'] + 1
            continue
        if -2 <= rate < 0:
            up_down_distribution['-2%~0%'] = up_down_distribution['-2%~0%'] + 1
            continue
        if 0 <= rate < 2:
            up_down_distribution['0%~2%'] = up_down_distribution['0%~2%'] + 1
            continue
        if 2 <= rate < 4:
            up_down_distribution['2%~4%'] = up_down_distribution['2%~4%'] + 1
            continue
        if 4 <= rate < 6:
            up_down_distribution['4%~6%'] = up_down_distribution['4%~6%'] + 1
            continue
        if 6 <= rate < 8:
            up_down_distribution['6%~8%'] = up_down_distribution['6%~8%'] + 1
            continue
        if rate >= 8:
            up_down_distribution['8%~涨停'] = up_down_distribution['8%~涨停'] + 1
            continue

    total = sum(up_down_distribution.values())
    distribution = {k: dict(count=v, prop=round(v / total * 100, 2)) for k, v in up_down_distribution.items()}

    median = numpy.median(rate_list)
    market_status = db['market_status']
    result = {}
    result['update'] = datetime.now()
    result['rate_median'] = float(median)
    result['distribution'] = distribution
    result['limit_up_stock'] = limit_up_stock
    result['limit_down_stock'] = limit_down_stock

    hour = date.hour
    min = date.minute if date.minute % 5 == 0 else (int(date.minute / 5) + 1) * 5
    if min == 60:
        min = 0
        hour = hour + 1
    dt = datetime(date.year, date.month, date.day, hour, min, 0)

    result['date'] = dt
    market_status.update_one({"date": dt}, {"$set": result}, upsert=True)


if __name__ == "__main__":
    # rps_analysis(datetime(2022, 5, 20), -250)
    # rps_analysis(datetime(2022, 5, 20), -120)
    # rps_analysis(datetime(2022, 5, 20), -60)
    # rps_analysis(datetime(2022, 5, 20), -30)
    # up_down_limit_analysis(datetime(2022, 5, 13))
    # market_status_analysis(datetime(2022, 4, 29,23,37,0))
    baotuan_analysis()

    print((int(56 / 5) + 1) * 5)
