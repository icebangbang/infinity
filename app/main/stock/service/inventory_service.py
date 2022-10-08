import pandas as pd

from app.main.db.mongo import db
from app.main.stock.service import board_service
from app.main.utils import date_util


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
            mean = group.dropna()['INVENTORY_YOY'].mean()
            inventory_data.update_one({"name":name,"date":date_util.parse_date_time(date)},
                                      {"$set":dict(date=date, value=mean,name=name)},
                                      upsert=True)


def get_market_inventory_info():
    """
    统计深市,沪市等市场的库存情况
    :return:
    """
    pass

if __name__ == "__main__":
    get_board_inventory_info()