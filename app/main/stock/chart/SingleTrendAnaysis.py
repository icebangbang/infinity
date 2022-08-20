import numpy

from app.main.stock.chart.Line import Line
from app.main.db.mongo import db
from app.main.utils import date_util
from datetime import datetime
import pandas as pd

from app.main.utils.date_util import WorkDayIterator


class SingleTrendAnaysis(Line):
    """
    趋势分析表
    """

    def generate(self, **kwargs):
        industry = kwargs['industry']

        legend = dict(
            data=['up','down','enlarge','convergence'],
            selected=dict(up=True,down=True,enlarge=False,convergence=False)
        )
        trend_data = db['trend_data']
        end = date_util.get_latest_work_day()
        start = date_util.get_work_day(end, 90)

        data_x = [date_util.date_time_to_str(date, "%m-%d") for date in WorkDayIterator(start, end)]

        trend_data_list = list(trend_data.find({"industry": industry,
                                                "date": {"$gte": start, "$lte": end},
                                                }))
        data_y_array = [dict(name="", y=[], yAxisIndex=0,markLine={}) for i in range(4)]
        index = 0
        df = pd.DataFrame(trend_data_list)
        for key, group in df.sort_values("date", ascending=True).groupby('trend'):
            data_y_array[index]['name'] = key
            for point in group.to_dict("records"):
                data_y_array[index]['y'].append(point['rate'])
            if key == 'up' or key == 'down':
                median = numpy.median(data_y_array[index]['y'])
                data_y_array[index]['markLine'] = {"data": [{"yAxis": median, "name": "中位数"}]}
            index = index + 1
        # y轴组合
        yAxis_array = [
            {
                "name": "数据",
                "type": 'value'
            }
        ]

        return dict(x=data_x, y_array=data_y_array, desc=industry, multiSerie=True,
                    yAxis_array=yAxis_array, legend=legend,
                    )


if __name__ == "__main__":
    trend = SingleTrendAnaysis()
    trend.generate(trend="up",
                   industryStart=0, industryEnd=10)
