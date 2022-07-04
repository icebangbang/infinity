from app.main.stock.api import stock_info
from app.main.db.mongo import db
import akshare as ak
from app.main.stock.dao import stock_dao
import logging

"""
同步公司各项指标
"""

def sync():
    stocks = stock_dao.get_all_stock()
    detail_set = db["stock_detail"]
    code_map = ak.code_id_map()

    for i,stock in enumerate(stocks):
        code = stock["code"]

        if code != "600091":continue

        logging.info("code {}:{}".format(code,i))
        df = ak.stock_ind(code, code_map)
        ind_dict = df.to_dict("records")[0]
        ind_dict['MarketValue'] = round(ind_dict['MarketValue']/100000000,2)
        ind_dict['flowCapitalValue'] = round(ind_dict['flowCapitalValue']/100000000,2)
        detail_set.update_one({"code":code},{"$set":ind_dict})



if __name__ == "__main__":
    sync()

