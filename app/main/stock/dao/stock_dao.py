from app.main.db.mongo import db
from typing import List


def get_all_stock():
    my_set = db['stock_detail']
    data = list(my_set.find({}, dict(code=1, date=1, belong=1, name=1, _id=0)))
    return data


def get_stock_detail(codes):
    my_set = db['stock_detail']
    data_list = list(my_set.find({"code": {"$in": codes}}))
    return {data['code']: data for data in data_list}



