import logging
from datetime import datetime

import akshare as ak

from app.main.db.mongo import db
from app.main.stock.dao import stock_dao
from app.main.utils import stock_util, date_util, collection_util

def sync_stock_gdfx():
    stock_detail_list = stock_dao.get_all_stock({"code": 1, "name": 1})

    stock_gdfx = db['stock_gdfx']
    for index, stock_detail in enumerate(stock_detail_list):
        code = stock_detail['code']
        name = stock_detail['name']
        code_str = stock_util.basic_belong(code) + code
        # date = date_util.get_report_day(datetime.now())
        date = datetime(2022,6,30)
        date_str = date_util.dt_to_str(date, "%Y%m%d")

        if "退" in name or "艾格" in name: continue
        result_list = list(stock_gdfx.find(dict(code=code, date=date)))
        if collection_util.is_not_empty(result_list):
            continue

        logging.info("[股东分析]{},同步{}，{},{}股东数据".format(index,code,name,date_str))
        stock_gdfx_free_top_10_em_df = ak.stock_gdfx_free_top_10_em(symbol=code_str, date=date_str)
        logging.info("[股东分析]{}，{},{}股东数据获取完毕".format(code, name, date_str))
        if stock_gdfx_free_top_10_em_df is None: continue
        stock_gdfx_free_top_10_em_df['code'] = code
        stock_gdfx_free_top_10_em_df['name'] = name
        stock_gdfx_free_top_10_em_df['date'] = date
        stock_gdfx_free_top_10_em_df['update'] = datetime.now()
        # gd_list = list(stock_gdfx_free_top_10_em_df['股东名称'])

        # total = list()
        # for gd in gd_list:
        #     if "养老" in gd:
        #         print(code,name,gd)
        #         total.append("{},{},{}".format(code,name,gd))
        stock_gdfx = db['stock_gdfx']
        for record in stock_gdfx_free_top_10_em_df.to_dict(orient="records"):

            stock_gdfx.update_one({"code": code, "date": date,"gd_name":record['gd_name']},
                                  {"$set": record},
                                  upsert=True)

if __name__ == "__main__":
    sync_stock_gdfx()

