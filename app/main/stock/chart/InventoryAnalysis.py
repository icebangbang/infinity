import numpy

from app.main.stock.chart.Line import Line
from app.main.db.mongo import db
from app.main.utils import date_util, cal_util
from datetime import datetime
import pandas as pd
import numpy as np

from app.main.utils.date_util import WorkDayIterator


class InventoryAnalysis(Line):
    """
    库存周期分析表
    """

    def mad(factor):
        me = np.median(factor)
        mad = np.median(abs(factor - me))
        # 求出3倍中位数的上下限制
        up = me + (3 * 1.4826 * mad)
        down = me - (3 * 1.4826 * mad)
        # 利用3倍中位数的值去极值
        factor = np.where(factor > up, up, factor)
        factor = np.where(factor < down, down, factor)
        return factor


    def generate(self, **kwargs):

        stock_balance = db['stock_balance']
        board_detail = db['board_detail']
        codes = board_detail.find_one({"board":"光伏设备"},{"codes":1})['codes']
        # data_list = list(stock_balance.find({"code":"600126"},{"INVENTORY_YOY":1,"date":1}))
        data_list = list(stock_balance.find({"code":{"$in":codes}},{"INVENTORY_YOY":1,"date":1,"code":1,"_id":0}))
        # data_x = [date_util.date_time_to_str(data['date'], "%Y-%m-%d") for data in data_list]
        df = pd.DataFrame(data_list)
        new_data_list =  []
        for date,group in df.groupby(['date']):
            n = group.dropna()['INVENTORY_YOY']

            me = np.median(n)
            mad = np.median(abs(n - me))
            up = me + (3 * 1.4826 * mad)
            down = me - (3 * 1.4826 * mad)
            n = np.where(n > up, up, n)
            n = np.where(n < down, down, n)
            new_data_list.append(dict(date=date,value=n.mean()))
        data_x = [data['date'] for data in new_data_list]
        data_y = [cal_util.round(data['value'],2) for data in new_data_list]
        data_y_array = [dict(name="单位(亿)", y=data_y)]
        yAxis_array = [
            {
                "name": "库存",
                "type": 'value'
            }
        ]
        return dict(x=data_x,
                    y_array=data_y_array,
                    yAxis_array=yAxis_array,
                    )


if __name__ == "__main__":

    trend = InventoryAnalysis()
    print(trend.generate(trend="up",
                   industryStart=0, industryEnd=10))
