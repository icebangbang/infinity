from app.main.db.mongo import db, myclient
from typing import List
from datetime import datetime

from app.main.stock.company import Company
from app.main.stock.job import job_config
from app.main.task.stock_task import sync_stock_k_line
from app.main.utils import date_util
import pymongo


def get_all_stock(fields=None,filter={}):
    if fields is None:
        fields = dict(code=1, date=1, belong=1, name=1, _id=0)
    my_set = db['stock_detail']
    data = list(my_set.find(filter, projection=fields))
    return data


def get_stock_detail(codes:list):
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


def get_code_name_map():
    my_set = db['stock_detail']
    data = list(my_set.find({}, dict(code=1, name=1, _id=0)))
    return {d["code"]: d["name"] for d in data}


def dump_stock_feature(companies: List[Company], date):
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

def clear_stock_info():
    """
    清空个股k线
    :return:
    """
    db['k_line_day'].drop()
    # db['k_line_month'].drop()
    # db.k_line_month.create_index([("date", 1), ("code", 1)])
    db.k_line_day.create_index([("code", 1)])
    db.k_line_day.create_index([("date", 1), ("code", 1)])
    db.k_line_day.create_index([("date", 1)])

    db['stock_feature'].drop()
    db.stock_feature.create_index([("code", 1)])
    db.stock_feature.create_index([("date", 1), ("code", 1)])

    job_config.acquire_job("app.main.task.stock_task.sync_stock_k_line")

    sync_stock_k_line.apply_async(kwargs=dict(reuild_data=True))





if __name__ == "__main__":
    # get_company_feature("689009", datetime(2021, 11, 1))
    # a = get_stock_detail(['159980'])
    clear_stock_info()
    print()