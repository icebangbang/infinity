from datetime import datetime

import pandas as pd

from app.main.model.board_value import BoardValue
from app.main.stock.chart.Line import Line
from app.main.stock.service import fund_service
from app.main.utils import date_util
from app.main.utils.date_util import WorkDayIterator


class BoardValueAnalysis(Line):
    """
    板块市值分析
    """

    def generate(self, **kwargs):
        day = kwargs.get("spanDay", 1)

        date_start = date_util.parse_from_dict(kwargs,"dateStart",datetime.now())
        date_end = date_util.parse_from_dict(kwargs,"dateEnd",datetime.now())
        # 得到最近的工作
        # date = date_util.get_latest_work_day(date)

        latest_day = None
        resp_dict = {}
        content = {}
        for date in WorkDayIterator(date_start,date_end):


            board_value_0: BoardValue = fund_service.get_stock_value_by_board(date)
            board_value_x: BoardValue = fund_service.get_stock_value_by_board(
                date_util.get_work_day(board_value_0.date, day))

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


            yAxisData = list(diff_lists[0].keys())
            xAxisData = []
            for k, v in diff_lists[0].items():
                xAxisData.append(dict(value=v, lable='right' if v < 0 else None))

            latest_day = date
            content[date_util.dt_to_str(date,"%Y-%m-%d")] = dict(yAxisData=yAxisData, xAxisData=xAxisData)

            # 生成日期
        start = date_util.get_work_day(latest_day, 90)
        day_range = [date_util.dt_to_str(day,"%Y-%m-%d") for day in WorkDayIterator(start, latest_day)]
        resp_dict['content'] = content
        resp_dict['dateEnd'] = date_util.dt_to_str(latest_day,"%Y-%m-%d")
        resp_dict['dayRange'] = day_range
        return resp_dict
