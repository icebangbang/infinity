import akshare as ak
import pandas as pd
from datetime import datetime
from app.main.db.mongo import db
from typing import List

from app.main.stock.api import stock_index

id_maps = {"sh000001": {"000001": 1, "code": "000001", "belong": "sh"},
           "zs399001": {"399001": 0, "code": "399001", "belong": "sz"}}


def sync_index_data(code, start_date, end_date, klt="101"):
    """
    同步a股指数
    :return:
    """
    id_map = id_maps[code]
    code = id_map["code"]
    data = stock_index.fetch_index_day_level(code, start_date, end_date, klt, id_map)
    data["belong"] = id_map["belong"]
    _dump_index_data(data.to_dict("records"))

    return data


def _dump_index_data(records: List):
    my_set = db['stock_index_k_line_day']
    my_set.insert_many(records)


def clear_index_data():
    my_set = db['stock_index_k_line_day']
    my_set.delete_many({})
