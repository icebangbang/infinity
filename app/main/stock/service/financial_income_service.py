"""
营业收入等统计
"""
import numpy as np
import pandas as pd

from app.main.db.mongo import db
from app.main.stock.service import board_service
from app.main.utils import date_util, cal_util
import logging
import json


def _echo(v):
    if "OPERATE_INCOME" in v.keys() and\
            v["OPERATE_INCOME"] != -99999: return v["OPERATE_INCOME"]
    if "TOTAL_OPERATE_INCOME" in v.keys() and \
            v["TOTAL_OPERATE_INCOME"] != -99999: return v["TOTAL_OPERATE_INCOME"]
    return None


def get_board_income_info():
    """
    统计行业板块中的收入数据
    :return:
    """
    boards = board_service.get_all_board()
    income_data = db['financial_income_data']
    stock_profit = db['stock_performance_profit']

    for board in boards:
        codes = board['codes']
        name = board['board']

        data_list = list(
            stock_profit.find({"code": {"$in": codes}}, {"OPERATE_INCOME": 1, "date": 1, "code": 1, "_id": 0}))

        df = pd.DataFrame(data_list)
        df.fillna(-99999, inplace=True)
        for date, group in df.groupby(['date']):
            filtered = [_echo(g) for g in group.to_dict(orient="records")]
            filtered = [f for f in filtered if f is not None]
            income_sum = np.median([f for f in filtered if f is not None])
            income_sum = cal_util.divide(income_sum, 100000000, 3)
            logging.info("同步板块{}的营业总收入的中位数:{},{}".format(name, date, income_sum))

            income_data.update_one({"name": name, "date": date_util.parse_date_time(date)},
                                   {"$set": dict(date=date_util.parse_date_time(date), total_income=income_sum,
                                                 name=name)},
                                   upsert=True)


if __name__ == "__main__":
    get_board_income_info()
