from app.main.stock.chart.Line import Line
from app.main.db.mongo import db
from app.main.utils import date_util
from datetime import datetime
import pandas as pd

from app.main.utils.date_util import WorkDayIterator


class TrendAnaysis(Line):
    """
    趋势分析表
    """

    def generate(self, **kwargs):
        industryStart = int(kwargs['industryStart'])
        industryEnd = int(kwargs['industryEnd'])
        trend = kwargs['trend']

        board_detail = db['board_detail']
        boards = board_detail.find({"type": 2}).sort("size",-1).skip(industryStart).limit(industryEnd - industryStart)
        industrys = [ board['board'] for board in boards]

        trend_data = db['trend_data']
        end = date_util.get_latest_work_day()
        start = date_util.get_work_day(end, 30)

        data_x = [date_util.date_time_to_str(date, "%m-%d") for date in WorkDayIterator(start, end)]

        trend_data_list = list(trend_data.find({"industry": {"$in": industrys},
                                                "date": {"$gte": start, "$lte": end},
                                                "trend": trend
                                                }))
        data_y_array = [dict(name="", y=[], yAxisIndex=0) for i in range(len(industrys))]
        index = 0
        df = pd.DataFrame(trend_data_list)
        for key, group in df.groupby(['industry']):
            data_y_array[index]['name'] = key
            for point in group.to_dict("records"):
                data_y_array[index]['y'].append(point['rate'])
            index = index + 1
        # y轴组合
        yAxis_array = [
            {
                "name": "数据",
                "type": 'value'
            }
        ]

        return dict(x=data_x, y_array=data_y_array, desc="板块趋势", multiSerie=True,
                    yAxis_array=yAxis_array, legend=industrys)


if __name__ == "__main__":
    trend = TrendAnaysis()
    trend.generate(trend="up",
                   industryStart=0,industryEnd=10)
