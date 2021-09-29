from app.main.db.mongo import db
from typing import List

from app.main.stock.company import Company


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
    data = list(my_set.find({}, dict(code=1, name=1,_id=0)))
    return {d["code"]:d["name"] for d in data}

def dump_stock_feature(companies:List[Company],date):
    my_set = db['stock_feature']
    features = [dict(code=company.code,name=company.name,date=date,features=company.features)
                for company in companies]
    my_set.insert_many(features)
