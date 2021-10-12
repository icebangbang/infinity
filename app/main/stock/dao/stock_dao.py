from app.main.db.mongo import db
from typing import List
from datetime import datetime

from app.main.stock.company import Company
from app.main.utils import date_util


def get_all_stock():
    my_set = db['stock_detail']
    data = list(my_set.find({}, dict(code=1, date=1, belong=1, name=1, _id=0)))
    return data


def get_stock_detail(codes):
    my_set = db['stock_detail']
    data_list = list(my_set.find({"code": {"$in": codes}}))
    return {data['code']: data for data in data_list}


def get_stock_detail_list(codes):
    my_set = db['stock_detail']
    data_list = list(my_set.find({"code": {"$in": codes}}))
    return data_list


def get_code_name_map():
    my_set = db['stock_detail']
    data = list(my_set.find({}, dict(code=1, name=1, _id=0)))
    return {d["code"]: d["name"] for d in data}


def dump_stock_feature(companies: List[Company], date):
    delete_stock_feature(date_util.get_start_of_day(datetime.now()))
    my_set = db['stock_feature']
    features = [dict(code=company.code, name=company.name, date=date, features=company.features)
                for company in companies]
    my_set.insert_many(features)


def delete_stock_feature(date):
    my_set = db['stock_feature']
    my_set.delete_many({"date": date})


def pick_by_feature(condition,date):
    c = {"features." + str(k): v for k, v in condition.items()}
    c['date'] = date_util.get_start_of_day(date)
    my_set = db['stock_feature']
    result = list(my_set.find(c,dict(code=1, name=1, _id=0)))
    return result
