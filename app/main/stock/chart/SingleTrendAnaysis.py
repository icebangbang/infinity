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
            data=['up', 'down', 'enlarge', 'convergence'],
            selected=dict(up=True, down=True, enlarge=False, convergence=False)
        )
        trend_data = db['trend_data']
        end = date_util.get_latest_work_day()
        start = date_util.get_work_day(end, 120)

        # 节气节点数据
        # time=时间, jq=节气, jq_index=节气下标
        jq_list = date_util.get_jq_list(start, end)
        mark_area = {
            "itemStyle": {
                "color": 'rgba(255, 173, 177, 0.4)'
            },
            'data': []
        }
        for i, jq in enumerate(jq_list):
            jq_name = jq['jq']+"(c)" if (i+1)%4 ==0 else jq['jq']
            jq_start = jq['time']
            jq_start = date_util.add_and_get_work_day(jq_start,1)
            if i + 1 >= len(jq_list):
                jq_end = end
            else:
                jq_end = jq_list[i + 1]['time']
            jq_end = date_util.get_latest_work_day(jq_end)
            mark_area['data'].append([dict(name=jq_name, xAxis=date_util.date_time_to_str(jq_start, "%m-%d")),
                                      dict(xAxis=date_util.date_time_to_str(jq_end, "%m-%d"))])

        # data_x = [date_util.date_time_to_str(date, "%m-%d") for date in WorkDayIterator(start, end)]
        data_x_format = []
        data_x = []
        fill_x_flag = True

        trend_data_list = list(trend_data.find({"industry": industry,
                                                "date": {"$gte": start, "$lte": end},
                                                }))
        data_y_array = [dict(name="", y=[], yAxisIndex=0, markLine={}) for i in range(4)]
        index = 0
        df = pd.DataFrame(trend_data_list)
        for key, group in df.sort_values("date", ascending=True).groupby('trend'):
            data_y_array[index]['name'] = key
            if key =='up':
                data_y_array[index]['markArea'] = mark_area
            for point in group.to_dict("records"):
                data_y_array[index]['y'].append(point['rate'])
                if fill_x_flag:
                    data_x.append(point['date'])
                    data_x_format.append(date_util.date_time_to_str(point['date'], "%m-%d"))
            fill_x_flag = False
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


            # time = jq['time']

        return dict(x=data_x_format, y_array=data_y_array, desc=industry, multiSerie=True,
                    yAxis_array=yAxis_array, legend=legend,
                    mark_area=mark_area,
                    )


if __name__ == "__main__":
    trend = SingleTrendAnaysis()
    trend.generate(trend="up",
                   industryStart=0, industryEnd=10)
