from datetime import datetime
from typing import List

import pymongo

from app.main.db.mongo import db
from app.main.stock.api import etf_info
from app.main.stock.company import Company
from app.main.utils import date_util
import logging as log


def get_eft_list():
    """
    获取合格的etf标的
    :return:
    """
    my_set = db['etf']
    return list(my_set.find({}))


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
    存储etf的信息,同时将名字通过分词切割
    存储关键字和关联信息到search_keyword_index中
    便于后续板块和对应的etf基金做关联
    :return:
    """
    etf_list = etf_info.get_etf_list()
    my_set = db['etf']
    search_keyword_index = db['search_keyword_index']

    for index, etf in enumerate(etf_list):
        code = etf['code']
        detail = etf_info.get_etf_detail(code)
        etf.update(detail)
        name = etf['name']
        etf['update_time'] = datetime.now()

        name_tag = detail['name_tag']
        for tag in name_tag:
            # 查找表中已有的记录
            result = search_keyword_index.find_one({"keyword": tag, "type": "etf"})
            # 判空并尝试新建集合
            result = result if result else {}
            result['keyword'] = tag
            result['type'] = "etf"
            # 获取keyword关联的信息
            refs = result.get("refs", [])
            # 新增关联信息,并做去重操作
            refs.append(name)
            result['refs'] = list(set(refs))
            # upsert操作
            search_keyword_index.update_one({"keyword": tag, "type": "etf"}, {"$set": result}, upsert=True)

        my_set.update({"code": etf['code']}, {"$set": etf}, upsert=True)
        log.info("同步etf基金:{},{}".format(code, name))


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


def dump_etf_feature(companies: List[Company], date):
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


def get_etf_by_tag(tag):
    """
    tag通过倒排索引,查找etf内容
    :param tag:
    :return:
    """
    search_keyword_index = db['search_keyword_index']
    etf = db['etf']
    result = search_keyword_index.find_one({"keyword": tag, "type": "etf"})
    if result and result.get("refs", None):
        items = list(etf.find({"name": {"$in": result['refs']}}).sort("body", -1))
        return items
    return []


if __name__ == "__main__":
    # dump_etf()
    # dump_history_kline()
    etfs = get_etf_by_tag("电池")
    for etf in etfs:
        print("{},{},{}".format(etf['name'], etf['body'], etf['code']))
