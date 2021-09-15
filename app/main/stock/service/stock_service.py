import logging
from datetime import datetime, timedelta

import pandas as pd

from app.main.stock.dao import stock_dao, k_line_dao
from app.main.utils import date_util


def publish(days=10, slice=30, code_list=None,stock_map=None):
    now = date_util.get_start_of_day(datetime.now())
    start,now = date_util.get_work_day(now,offset=days)

    if code_list is None:
        stocks = stock_dao.get_all_stock()
    else:
        stocks = stock_dao.get_stock_detail_list(code_list)

    rise = []
    result_dict = dict()
    name_dict = dict()
    for stock in stocks:
        name_dict[stock['code']] = stock['name']

    page_size = 100
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
        k_list = k_line_dao.get_k_line_by_code(temp_code_list, start, now)
        for k in k_list:
            result_dict[k['code']].append(k)
        for k, v in result_dict.items():
            if len(v) > 0:
                if len(v) == 1:
                    earliest = v[0]["open"]
                    latest = v[0]["close"]
                    c = (latest - earliest) / earliest
                else:
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
        print("{} {} {} {}".format(i['code'], i['name'], i['rise'],get_concepts(stock_map,i['code'])))

    print("跌幅前{}是:".format(slice))
    for i in bot:
        print("{} {} {} {}".format(i['code'], i['name'], i['rise'],get_concepts(stock_map,i['code'])))

def get_concepts(stock_map,code):
    if code in stock_map.keys():
        return stock_map[code]['board']
    return ""

if __name__ == "__main__":
    publish(2,10)