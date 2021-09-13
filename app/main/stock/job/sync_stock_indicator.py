from app.main.stock.api import stock_info
from app.main.db.mongo import db
import akshare as ak
from app.main.stock.dao import stock_dao
import logging

"""
同步公司各项指标
"""

stocks = stock_dao.get_all_stock()
ind_set = db["stock_indicator"]
ind_list = []
code_map = ak.code_id_map()

for i,stock in enumerate(stocks):
    logging.info("code {}:{}".format(stock["code"],i))
    df = ak.stock_ind(stock['code'], code_map)
    ind_dict = df.to_dict("records")[0]
    ind_list.append(ind_dict)

ind_set.remove()
ind_set.insert_many(ind_list)
