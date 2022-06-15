from app.main.stock.chart.Line import Line
from app.main.db.mongo import db
from app.main.utils import date_util
from datetime import datetime


class BoardKLine(Line):
    """
    """

    def generate(self, **kwargs):
        board_k_line_day = db['board_k_line_day']
        boardName = kwargs['boardName']
        start = date_util.get_work_day(datetime.now(), 30)
        # 获取所有数据点位
        data_list = list(board_k_line_day.find({"name": boardName, "date": {
            "$gte": start,
            "$lte": datetime.now()
        }}))
        data_x = [date_util.date_time_to_str(data['date'], "%Y-%m-%d") for data in data_list]
        y = [[data['open'], data['close'], data['low'], data['high']] for data in data_list]

        yAxis_array = [
            {
                "name": "抱团比例",
                "type": 'value'
            }
        ]
        return dict(
            xAxis={
                "show": False,
                "data": data_x
            },
            yAxis={
                "show": False,
            },
            series=[
                {
                    "type": 'candlestick',
                    "data": y}
            ]

        )
