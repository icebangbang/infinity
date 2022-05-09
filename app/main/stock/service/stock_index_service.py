import akshare as ak
import pandas as pd
from datetime import datetime
from app.main.db.mongo import db
from typing import List

from app.main.stock.api import stock_index
from app.main.stock.dao import k_line_dao

id_maps = {"sh000001": {"000001": 1, "code": "000001", "belong": "sh", "name": "上证指数"},
           "zs399001": {"399001": 0, "code": "399001", "belong": "sz", "name": "深证指数"},
           "zs399106": {"399106": 0, "code": "399106", "belong": "sz", "name": "深证综指"},
           "zs399006": {"399006": 0, "code": "399006", "belong": "sz", "name": "创业板指数"},
           "BDI": {"BDI": 100, "code": "BDI", "belong": "BDI", "name": "波罗的海bdi指数"}
           }


def sync_index_data(code, start_date, end_date, klt="101"):
    """
    同步a股指数
    :return:
    """
    id_map = id_maps[code]
    code = id_map["code"]
    data = stock_index.fetch_index_day_level(code, start_date, end_date, klt, id_map)

    if data is None:
        return None

    data["belong"] = id_map["belong"]
    data["name"] = id_map["name"]

    if data.empty is not True:
        _dump_index_data(data.to_dict("records"))

    return data


def _dump_index_data(records: List):
    my_set = db['stock_index_k_line_day']
    my_set.drop()
    my_set.insert_many(records)


def clear_index_data():
    my_set = db['stock_index_k_line_day']
    my_set.delete_many({})


def get_index_k_line(from_date, to_date):
    daily_price = pd.DataFrame(k_line_dao.get_index_kline_data(from_date, to_date))
    return daily_price

