from app.main.stock.api import stock_change
from app.main.stock.dao import stock_dao
from datetime import datetime, timedelta
from app.main.db.mongo import db
import logging

from app.main.utils import date_util

stocks = stock_dao.get_all_stock()
stock_change_collection = db["stock_change"]
stock_change_collection.delete_many({})

now = datetime.now()
for index, stock in enumerate(stocks):
    result_list = list()
    code = stock['code']
    belong = stock['belong']
    logging.info("{} {}".format(index, code))

    for i in range(5):
        t = now - timedelta(days=i)
        if date_util.is_weekend(t): continue
        if now == t and t.hour < 15: continue

        if belong == 'sh': market = 1
        if belong == 'sz': market = 0

        df = stock_change.get_stock_changes(code, t, market)
        if df is None: continue
        result_list.extend(df.to_dict("records"))
    if len(result_list) > 0:
        stock_change_collection.insert_many(result_list)
