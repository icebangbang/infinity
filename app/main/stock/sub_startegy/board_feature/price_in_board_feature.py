import logging
from decimal import Decimal

from backtrader.feeds import PandasData

from app.main.stock import constant
from app.main.stock.company import Company
from app.main.stock.dao import board_dao, k_line_dao
from app.main.stock.sub_startegy import BoardSubST
from datetime import datetime
import pandas as pd

from app.main.utils import cal_util


class PriceInBoardFeature(BoardSubST):
    """
    """


    def run(self, date, name):
        """
        :return:
        """
        # total_kline_list = k_line_dao.get_k_line_data(date, date, 'day')
        # total_close_list = [k_line['close'] for k_line in total_kline_list]
        # total_close_max = max(total_close_list)
        # total_close_min = min(total_close_list)
        # df = pd.DataFrame(total_kline_list)
        # df2 = pd.pivot_table(df, values=['code'], index=['cut'],
        #                       aggfunc={'code': lambda x: len(x.dropna().unique())}
        #                       , fill_value=0).reset_index(drop=False)  # fill_value = 0是用来填充缺失值、空值
        # df2 = df2.rename(columns={'订单号': '订单数'})



        board = board_dao.get_board_by_name(name)
        codes = board['codes']
        # 获取当天的数据
        kline_list = k_line_dao.get_k_line_data(date, date, 'day', codes)
        # 获取收盘价
        close_list = [k_line['close'] for k_line in kline_list]

        df = pd.DataFrame(kline_list)
        df['range'] = pd.cut(df.close, bins=[0, 5, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000],
                           labels=["0-5", "5-10", "10-20", "20-30", "30-40", "40-50", "50-100", "100-200", "200-300",
                                   "300-400", "400-500", "500-1000", "1000-2000"],
                           include_lowest=False)
        agg_df = pd.pivot_table(df, values=['code'], index=['range'],
                              aggfunc={'code': lambda x: len(x.dropna().unique())}
                              # aggfunc={'code': lambda x: cal_util.round(len(x.dropna().unique())/len(df),2)}
                              , fill_value=0).reset_index(drop=False)  # fill_value = 0是用来填充缺失值、空值
        agg_df = agg_df.rename(columns={'code': 'sum'})
        agg_df['total'] = len(agg_df)

        return {"price_range":agg_df.to_dict(orient="records")}



if __name__ == "__main__":
    f = PriceInBoardFeature()
    f.run(datetime(2019,1,2),"煤炭行业")

