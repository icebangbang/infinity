from datetime import datetime
from typing import List

import pymongo

from app.main.db.mongo import db, myclient
from app.main.stock.api import etf_info
from app.main.stock.company import Company
from app.main.utils import date_util


def get_eft_list():
    """
    获取合格的etf标的
    :return:
    """
    my_set = db['etf']
    return my_set.find({})



def get_code_name_map():
    """
    获取code,name映射字典
    :return:
    """
    etfs = get_eft_list()
    code_name_map = {etf['code']: etf['name'] for etf in etfs}
    return code_name_map


def dump_etf():
    """
    存储etf的信息
    :return:
    """
    etf_list = etf_info.get_all_etf()
    my_set = db['etf']

    for etf in etf_list:
        my_set.update({"code": etf['code']}, {"$set": etf}, upsert=True)


def dump_history_kline():
    """
    存储历史k线
    :return:
    """
    db.etf_kline_day.drop()
    db.etf_kline_day.create_index([("code", 1)])
    db.etf_kline_day.create_index([("date", -1), ("code", 1)])

    etf_set = db['etf']
    etf_kline_day = db['etf_kline_day']
    etf_list = etf_set.find({})
    for etf in etf_list:
        print(etf['code'])
        kline_data = etf_info.fetch_kline_data(etf['code'])
        etf_kline_day.insert_many(kline_data)

def dump_stock_feature(companies: List[Company], date):
    start_of_day = date_util.get_start_of_day(date)

    my_set = db['etf_feature']
    update = []

    for company in companies:
        # features.append(dict(code=company.code, name=company.name, date=start_of_day, features=company.features))
        update.append(pymongo.UpdateMany({'code': company.code, 'date': start_of_day}, {"$set": {
            "code": company.code, "name": company.name, "date": start_of_day, "features": company.features,
            "update": datetime.now()
        }}, True))
    my_set.bulk_write(update)


if __name__ == "__main__":
    dump_history_kline()
