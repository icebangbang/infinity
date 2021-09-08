from datetime import datetime, timedelta
import pandas as pd

from app.main.stock.dao import k_line_dao, stock_dao
from app.main.utils import date_util

stocks = stock_dao.get_all_stock()
import logging

def publish(days=10,slice=30):
    now = date_util.get_start_of_day(datetime.now())
    start = now - timedelta(days=days)

    rise = []
    code_list = [100]
    result_dict = dict()

    name_dict = {stock['code']:stock['name'] for stock in stocks}

    for index,stock in enumerate(stocks):
        code_list.append(stock['code'])
        result_dict[stock['code']] = []
        if len(code_list) == 100:
            logging.info("current index is {}".format(index))
            k_list = k_line_dao.get_k_line_by_code(code_list, start, now)
            for k in k_list:
                result_dict[k['code']].append(k)
            for k, v in result_dict.items():
                if len(v) > 0:
                    earliest = v[0]["close"]
                    latest = v[-1:][0]["close"]
                    c = (latest - earliest) / earliest
                    rise.append((k,name_dict[k], c))
            code_list.clear()
            result_dict.clear()


    rise = pd.DataFrame(rise)
    rise.columns = ['code','name','rise']
    rise = rise.sort_values(by='rise', ascending=False)
    new = rise.to_dict("records")

    top = new[0:slice]

    rise = rise.sort_values(by='rise', ascending=True)
    new = rise.to_dict("records")

    bot = new[-slice:]

    print("涨幅前{}是:".format(slice))
    for i in top:
        print("{} {} {}".format(i['code'],i['name'],i['rise']))

    print("跌幅前{}是:".format(slice))
    for i in bot:
        print("{} {} {}".format(i['code'], i['name'], i['rise']))

publish(2,30)