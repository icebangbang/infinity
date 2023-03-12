from datetime import datetime
from typing import List

import pymongo

from app.log import get_logger
from app.main.db.mongo import db
from app.main.stock.api import etf_info
from app.main.stock.company import Company
from app.main.utils import date_util

log = get_logger(__name__)


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


def dump_etf_hold():
    """
    以季度为单位保存基金的个股持仓情况
    :return:
    """
    etf_list = etf_info.get_etf_list()
    etf_hold = db['etf_hold']

    # 获取当前最近的报告季，以及季度的index
    latest_report_day, season = date_util.get_report_day(datetime.now())

    log.info("[etf基金]总同步数:{}".format(len(etf_list)))

    for index, etf in enumerate(etf_list):
        fund_code = etf['code']
        fund_name = etf['name']
        log.info("[etf基金]同步etf基金的持仓情况:{},{},{}".format(fund_code, fund_name, index))
        holds = etf_info.get_etf_hold(fund_code, fund_name)

        for hold in holds:
            hold_code = hold['code']
            etf_hold.update_one({"fund_code": fund_code, "season": season, "code": hold_code}, {"$set": hold},
                                upsert=True)


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
        log.info("[etf基金]同步etf基金信息:{},{}".format(code, name))


def get_etf_kline_day(code, start, end):
    """
    获取场内etf基金的日k线数据
    :return:
    """
    etf_kline_day = db['etf_kline_day']
    data_points = list(etf_kline_day.find({"code": code,
                                           "date": {"$gte": start, "$lte": end}},
                                          {"close": 1, "open": 1, "high": 1, "low": 1, "date": 1, "money": 1}
                                          ))
    return data_points


def dump_history_kline():
    """
    存储历史k线
    :return:
    """
    etf_set = db['etf']
    etf_kline_day = db['etf_kline_day']
    etf_list = list(etf_set.find({}))
    total_etf = len(etf_list)
    for index, etf in enumerate(etf_list):
        log.info(
            "[etf基金]同步eft基金k线信息：{},{},index:{},total:{}".format(etf['code'], etf['name'], index, total_etf))
        code = etf['code']
        kline_data_list = etf_info.fetch_kline_data(code, etf['belong'])
        for kline_data in kline_data_list:
            etf_kline_day.update_one({"code": code, "date": kline_data['date']}, {"$set": kline_data}, upsert=True)


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


def get_etf_by_code(fund_code):
    """
    通过基金代码获取基金信息
    :param fund_code:
    :return:
    """
    etf_set = db['etf']
    etf = etf_set.find_one({"code": fund_code})
    return etf


def get_related_etf(codes):
    """
    通过个股代码查找记录
    :param codes:
    :return:
    """
    etf_hold = db['etf_hold']
    holds = list(etf_hold.find({"code": {"$in": codes}}))
    return holds


if __name__ == "__main__":
    # dump_etf()
    # dump_etf_hold()
    dump_history_kline()
    # etfs = get_etf_by_tag("电池")
    # for etf in etfs:
    #     print("{},{},{}".format(etf['name'], etf['body'], etf['code']))
