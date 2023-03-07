from datetime import datetime
from typing import List

import pymongo

from app.main.db.mongo import db
from app.main.stock.company import Company
from app.main.utils import date_util, collection_util


def get_all_stock(fields=None, filter={}):
    if fields is None:
        fields = dict(code=1, date=1, belong=1, name=1, _id=0)
    my_set = db['stock_detail']
    data = list(my_set.find(filter, projection=fields))
    return data


def get_stock_detail(codes: list):
    """
    获取一组个股详情数据
    :param codes:
    :return:
    """
    my_set = db['stock_detail']
    data_list = list(my_set.find({"code": {"$in": codes}}))
    return {data['code']: data for data in data_list}


def get_stock_detail_by_code(code):
    """
    获取单独个股详情
    :param code:
    :return:
    """
    my_set = db['stock_detail']
    data = my_set.find_one({"code": code})
    return data


def get_stock_detail_by_name(name):
    """
    获取单独个股详情
    :param code:
    :return:
    """
    my_set = db['stock_detail']
    data = my_set.find_one({"name": name})
    return data


def get_one_stock(code):
    my_set = db['stock_detail']
    return my_set.find_one({"code": code})


def get_stock_detail_list(codes=None, fields=None):
    condition = {}
    my_set = db['stock_detail']
    if fields is None:
        fields = {"_id": 0}
    if codes is not None:
        condition = {"code": {"$in": codes}}

    data_list = list(my_set.find(condition, projection=fields))
    return data_list


def get_stock_detail_map(codes=None, fields=None) -> dict:
    data_list = get_stock_detail_list(codes, fields)
    return {data['code']: data for data in data_list}


def get_code_name_map():
    """
    获取个股代码和名称的映射
    :return: {"code":"name"}
    """
    my_set = db['stock_detail']
    data = list(my_set.find({}, dict(code=1, name=1, _id=0)))
    return {d["code"]: d["name"] for d in data}


def get_code_province_map():
    """
    获取个股代码和省份的映射
    :return: {"code":"province"}
    """
    my_set = db['stock_detail']
    data_list = list(my_set.find({}, dict(code=1, name=1, board=1, _id=0, province=1)))
    code_province_dict = {}
    for data in data_list:
        province = data['province'] if data['province'] is not None else "海外"
        code = data['code']
        # 目前已知的，是中芯国际，九号公司等经营芯片，医药的高科技公司
        code_province_dict[code] = province

    return code_province_dict


def dump_stock_feature(companies: List[Company], date):
    """
    保存个股特征
    :param companies: 公司维度的特征数据
    :param date:
    :return:
    """
    start_of_day = date_util.get_start_of_day(date)

    my_set = db['stock_feature']
    update = []

    for company in companies:
        # features.append(dict(code=company.code, name=company.name, date=start_of_day, features=company.features))
        update.append(pymongo.UpdateMany({'code': company.code, 'date': start_of_day}, {"$set": {
            "code": company.code, "name": company.name, "date": start_of_day, "features": company.features,
            "update": datetime.now()
        }}, True))
    my_set.bulk_write(update)

def get_latest_stock_feature():
    """
    获取最近同步的个股特征数据
    :return:
    """
    my_set = db['stock_feature']
    points = list(my_set.find({}).sort("update_time", -1).limit(1))
    if collection_util.is_not_empty(points):
        return points[0]
    return None



def delete_stock_feature(date):
    my_set = db['stock_feature']
    my_set.delete_many({"date": date})


def pick_by_feature(condition, date):
    c = {"features." + str(k): v for k, v in condition.items()}
    c['date'] = date_util.get_start_of_day(date)
    my_set = db['stock_feature']
    result = list(my_set.find(c, dict(code=1, name=1, _id=0)))
    return result


def get_company_feature(code, date):
    """
    获取公司在某一日的数据特征
    :param date:
    :return:
    """
    my_set = db['stock_feature']
    result = my_set.find_one({"code": code, "date": date})
    if result is None: return {}
    # company = Company.load(code, result['name'], result['features'])
    return result['features']


if __name__ == "__main__":
    # get_company_feature("689009", datetime(2021, 11, 1))
    # a = get_stock_detail(['159980'])
    a = get_code_province_map()
    print()
