from datetime import datetime, timedelta

from app.main.utils import date_util
from app.main.stock.dao import stock_dao, k_line_dao
from collections import OrderedDict
import dateutil
from app.main.db.mongo import db
import logging


def baotuan_analysis():
    """
    包团分析
    :return:
    """
    start_time = datetime(2020, 1, 1)
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
        storage.append(dict(date=start_time,percent=percent))
        logging.info("[baotuan analysis] start month:{}:".format(date_util.dt_to_str(start_time), percent))
        start_time = next
    set = db['baotuan_analysis']
    set.drop()
    set.insert_many(storage)


if __name__ == "__main__":
    baotuan_analysis()
