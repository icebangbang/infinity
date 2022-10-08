import pandas as pd

from app.main.db.mongo import db
from app.main.stock.service import board_service
from app.main.utils import date_util, stock_util
import numpy as np


def get_board_inventory_info():
    """
    统计板块中的库存数据
    :return:
    """
    boards = board_service.get_all_board()
    inventory_data = db['inventory_data']
    stock_balance = db['stock_balance']
    for board in boards:
        codes = board['codes']
        name = board['board']

        # data_list = list(stock_balance.find({"code":"600126"},{"INVENTORY_YOY":1,"date":1}))
        data_list = list(
            stock_balance.find({"code": {"$in": codes}}, {"INVENTORY_YOY": 1, "date": 1, "code": 1, "_id": 0}))
        # data_x = [date_util.date_time_to_str(data['date'], "%Y-%m-%d") for data in data_list]
        df = pd.DataFrame(data_list)
        for date, group in df.groupby(['date']):
            if "INVENTORY_YOY" not in group.columns:
                print(name)
                continue
            print(date,name)
            n = group.dropna()['INVENTORY_YOY']
            me = np.median(n)
            mad = np.median(abs(n - me))
            up = me + (3 * 1.4826 * mad)
            down = me - (3 * 1.4826 * mad)
            n = np.where(n > up, up, n)
            n = np.where(n < down, down, n)
            inventory_data.update_one({"name": name, "date": date_util.parse_date_time(date)},
                                      {"$set": dict(date=date_util.parse_date_time(date), value=n.mean(), name=name)},
                                      upsert=True)


def get_market_inventory_info():
    """
    统计深市,沪市等市场的库存情况
    :return:
    """
    stock_balance = db['stock_balance']
    inventory_data = db['inventory_data']
    r = stock_balance.find({}, {"INVENTORY_YOY": 1, "_id": 0, "code": 1, "date": 1})
    df = pd.DataFrame(r)
    df['market'] = df.apply(lambda row: stock_util.market_belong(row['code']), axis=1)
    groups = df.groupby(['date', 'market'])
    for key, group in groups:
        n = group.dropna()['INVENTORY_YOY']

        me = np.median(n)
        mad = np.median(abs(n - me))
        up = me + (3 * 1.4826 * mad)
        down = me - (3 * 1.4826 * mad)
        n = np.where(n > up, up, n)
        n = np.where(n < down, down, n)
        date = key[0]
        name = key[1]
        inventory_data.update_one({"name": name, "date": date_util.parse_date_time(date)},
                                  {"$set": dict(date=date_util.parse_date_time(date), value=n.mean(), name=name)},
                                  upsert=True)


def _mad(factor):
    me = np.median(factor)
    mad = np.median(abs(factor - me))
    # 求出3倍中位数的上下限制
    up = me + (3 * 1.4826 * mad)
    down = me - (3 * 1.4826 * mad)
    # 利用3倍中位数的值去极值
    factor = np.where(factor > up, up, factor)
    factor = np.where(factor < down, down, factor)
    return factor


if __name__ == "__main__":
    get_board_inventory_info()
    get_market_inventory_info()
