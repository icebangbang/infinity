import json

from app.main.db.mongo import db
from app.main.stock.api import stock_info
from app.main.stock.dao import stock_dao
import logging as log

def update_stock_address():
    """
    更新个股的地址和官网信息
    :return:
    """
    stock_list = stock_dao.get_all_stock(dict(code=1, date=1, belong=1, name=1, _id=0,province=1))
    stock_dict = {v['code']: v for v in stock_list}

    stock_detail = db["stock_detail"]

    for code in stock_dict.keys():
        name = stock_dict[code]['name']
        province = stock_dict[code].get('province',None)
        if province: continue

        log.info("[同步个股详情]:同步地址,{},{}".format(code,name))
        try:
            reg_address = stock_info.get_stock_register_address(stock_dict[code])
            log.info("[同步个股详情]:地址详情{}".format(json.dumps(reg_address,ensure_ascii=False)))
            stock_dict[code].update(reg_address)
            stock_detail.update_one({"code": code}, {"$set": stock_dict[code]}, upsert=True)
        except Exception as e:
            log.error("[同步个股详情]:同步出错{}".format(code))
            log.error(e, exc_info=1)

if __name__ == "__main__":
    update_stock_address()