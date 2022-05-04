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
        storage.append(dict(date=start_time, percent=percent))
        logging.info("[baotuan analysis] start month:{}:".format(date_util.dt_to_str(start_time), percent))
        start_time = next
    set = db['baotuan_analysis']
    set.drop()
    set.insert_many(storage)


def market_status_analysis(date=datetime.now()):
    """
    涨跌情况分析
    :return:
    """
    if date_util.is_workday(date) is False: return
    now = date_util.get_start_of_day(date)
    stocks = stock_dao.get_all_stock(dict(code=1, name=1, _id=0))
    st_stock = {stock['code']: stock['name'] for stock in stocks if "ST" in stock['name']}
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
    for key, trade_data in groups.items():
        # close_1 = trade_data_list[0]['close']
        # close_2 = trade_data_list[1]['close']
        close_2 = trade_data['close']
        close_1 = trade_data['prev_close']
        rate = Decimal((close_2 - close_1) / close_1 * 100).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
        rate_list.append(rate)

        if key.startswith("3") or key.startswith("688"):
            if Decimal(close_1 * 1.2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                # 20cm
                up_down_distribution['涨停'] = up_down_distribution['涨停'] + 1
                continue
        else:
            if key in st_stock.keys() and Decimal(close_1 * 1.05).quantize(Decimal("0.01"),
                                                                           rounding="ROUND_HALF_UP").compare(
                Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                up_down_distribution['涨停'] = up_down_distribution['涨停'] + 1
                continue
            elif Decimal(close_1 * 1.1).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                up_down_distribution['涨停'] = up_down_distribution['涨停'] + 1
                continue

        if key.startswith("3") or key.startswith("688"):
            if Decimal(close_1 * 0.8).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                # 20cm
                up_down_distribution['跌停'] = up_down_distribution['跌停'] + 1
                continue
        else:
            if key in st_stock.keys() and Decimal(close_1 * 0.95).quantize(Decimal("0.01"),
                                                                           rounding="ROUND_HALF_UP").compare(
                Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                up_down_distribution['跌停'] = up_down_distribution['跌停'] + 1
                continue
            elif Decimal(close_1 * 0.9).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                up_down_distribution['跌停'] = up_down_distribution['跌停'] + 1
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
    result['date'] = now
    result['update'] = datetime.now()
    result['rate_median'] = float(median)
    result['distribution'] = distribution

    min = date.minute if date.minute % 5 == 0 else (int(date.minute / 5) + 1) * 5
    dt = datetime(date.year,date.month,date.day,date.hour,min,0)
    market_status.update_one({"date": dt}, {"$set": result}, upsert=True)


if __name__ == "__main__":
    baotuan_analysis()
    # market_status_analysis(datetime(2022, 4, 29,23,37,0))
