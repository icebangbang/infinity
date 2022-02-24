import logging
from datetime import datetime, timedelta

import pandas as pd

from app.main.stock.dao import stock_dao, k_line_dao
from app.main.stock.stock_pick_filter import stock_filter
from app.main.utils import date_util
from app.main.stock.stock_kline import id_map
import akshare as ak
from app.main.db.mongo import db
from app.main.stock.task_wrapper import TaskWrapper


def publish(days=10, slice=30, code_list=None, stock_map={}, start=None, end=None):
    if start is None and end is None:
        end = date_util.get_start_of_day(datetime.now())
        start, end = date_util.get_work_day(end, offset=days)

    if code_list is None:
        stocks = stock_dao.get_all_stock()
    else:
        stocks = stock_dao.get_stock_detail_list(code_list)

    rise = []
    result_dict = dict()
    name_dict = dict()
    for stock in stocks:
        name_dict[stock['code']] = stock['name']

    page_size = 200
    start_index = 0
    end_index = page_size
    flag = False

    while flag is False:
        logging.info("current index is {}".format(start_index))
        if end_index < len(stocks):
            inner = stocks[start_index:end_index]
            start_index = end_index
            end_index = end_index + page_size
        else:
            inner = stocks[start_index:]
            flag = True
        temp_code_list = [item['code'] for item in inner]
        result_dict = {item['code']: [] for item in inner}
        k_list = k_line_dao.get_k_line_by_code(temp_code_list, start, end)
        for k in k_list:
            result_dict[k['code']].append(k)
        for k, v in result_dict.items():
            if len(v) > 0:
                if len(v) == 1:
                    earliest = v[0]["open"]
                    latest = v[0]["close"]
                    c = (latest - earliest) / earliest
                else:
                    if v[0]['code'] == '300882':
                        print(123)
                    earliest = v[0]["close"]
                    latest = v[-1:][0]["close"]
                    c = (latest - earliest) / earliest
                rise.append((k, name_dict[k], c))
        result_dict.clear()

    rise = pd.DataFrame(rise)
    rise.columns = ['code', 'name', 'rise']
    rise = rise.sort_values(by='rise', ascending=False)
    new = rise.to_dict("records")

    top = new[0:slice]

    rise = rise.sort_values(by='rise', ascending=True)
    new = rise.to_dict("records")

    bot = new[0:slice]

    print("涨幅前{}是:".format(slice))
    for i in top:
        print("{} {} {} {}".format(i['code'], i['name'], round(i['rise'] * 100, 3), get_concepts(stock_map, i['code'])))

    print("跌幅前{}是:".format(slice))
    for i in bot:
        print("{} {} {} {}".format(i['code'], i['name'], round(i['rise'] * 100, 3), get_concepts(stock_map, i['code'])))


def get_concepts(stock_map, code):
    if code in stock_map.keys():
        return stock_map[code]['board']
    return ""


def sync_stock_ind(codes, task_wrapper: TaskWrapper = None):
    stock_detail_set = db["stock_detail"]
    stock_value_set = db["stock_value"]
    print("code size {}".format(len(codes)))
    for code in codes:
        now = datetime.now()
        start_of_day = date_util.get_start_of_day(now)
        df = ak.stock_ind(code, id_map)
        ind_dict = df.to_dict("records")[0]
        ind_dict['MarketValue'] = round(ind_dict['MarketValue'] / 100000000, 2)
        ind_dict['flowCapitalValue'] = round(ind_dict['flowCapitalValue'] / 100000000, 2)
        ind_dict['update_time'] = now
        stock_detail_set.update_one({"code": code}, {"$set": ind_dict})

        stock_value_set.update_one({"code": code, "date": start_of_day},
                                   {"$set": dict(
                                       MarketValue=ind_dict['MarketValue'],
                                       flowCapitalValue=ind_dict['flowCapitalValue'],
                                       update_time=now),
                                   }, upsert=True)

        if task_wrapper is not None:
            task_wrapper.trigger_count()


if __name__ == "__main__":
    # stocks = stock_dao.get_all_stock(dict(code=1))
    # code_name_map = stock_dao.get_code_name_map()
    # to_time = datetime.now()
    # from_time = to_time - timedelta(739)
    # stock_filter.get_stock_status(from_time, to_time)
    # publish(3, 100)

    stock_value_set = db["stock_value"]
    stock_value_set.update_one({"code": "300763", "date": datetime.now()},
                               {"$set": dict(
                                   MarketValue=0,
                                   flowCapitalValue=0,
                                   update_time=datetime.now()),
                               }, True)
