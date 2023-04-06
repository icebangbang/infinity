from datetime import datetime, timedelta

import pandas as pd

from app.main.model.board_value import BoardValue
from app.main.stock.chart.Line import Line
from app.main.stock.service import fund_service
from app.main.utils import date_util


class BoardValueAnalysis(Line):
    """
    板块市值分析
    """

    def generate(self, **kwargs):
        day = kwargs.get("spanDay", 1)

        board_value_0: BoardValue = fund_service.get_stock_value_by_board(datetime.now())
        board_value_x: BoardValue = fund_service.get_stock_value_by_board(date_util.get_work_day(board_value_0.date,day))

        board_value_0 = board_value_0.value
        board_value_x = board_value_x.value

        # 重排序
        board_value_x = {k: board_value_x.get(k) for k, v in board_value_0.items()}

        df0 = pd.DataFrame([board_value_0])
        df5 = pd.DataFrame([board_value_x])

        # 两个df相减
        diff = df0 - df5
        diff_lists = diff.to_dict(orient="records")
        in_board = {k: v for k, v in diff_lists[0].items() if v >= 0}
        out_board = {k: v for k, v in diff_lists[0].items() if v < 0}

        r = {}

        yAxisData = list(diff_lists[0].keys())
        xAxisData = []
        for k,v in diff_lists[0].items():

            xAxisData.append(dict(value=v,lable='right' if v<0 else None))



        return dict(yAxisData=yAxisData,xAxisData=xAxisData)
