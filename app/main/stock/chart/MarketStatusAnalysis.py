from app.main.stock.chart.Line import Line
from app.main.db.mongo import db
from app.main.utils import date_util
from datetime import datetime


class MarketStatusAnalysis(Line):
    """
    市场涨跌情况分析图表
    """

    def generate(self,**kwargs):
        market_status = db['market_status']
        latest_point = market_status.find_one({},sort=[('date',-1)])
        if latest_point is None:
            now = datetime.now()
        else:
            now = latest_point['date']
        # now = datetime(2022, 4, 29)
        start = date_util.get_start_of_day(now)
        end = date_util.get_end_of_day(now)
        # 获取所有数据点位
        data_list = list(market_status.find({"date": {"$lte": end, "$gte": start}}))
        data_x = [date_util.date_time_to_str(data['date'], "%H:%M") for data in data_list]
        data_y_array = [dict(name="", y=[], yAxisIndex=0) for i in range(12)]

        # y轴组合
        yAxis_array = [
            {
                "name": "家数",
                "type": 'value'
            },
            {
                "name": '涨跌中位数',
                "type": 'value',
            }
        ]

        median_value = []
        for data in data_list:
            # data 是每n分钟的时间点数据
            index = 0
            median_value.append(data['rate_median'])
            for key, item in data["distribution"].items():
                # key 跌停,跌停~8%,-8%~-6%
                count = item['count']
                data_y_array[index]['y'].append(count)
                data_y_array[index]['name'] = key
                index = index + 1

        data_y_array.append(dict(name="涨幅中位数", y=median_value, yAxisIndex=1,lineStyle="dashed"))

        return dict(x=data_x, y_array=data_y_array, desc="个股涨跌走势", multiSerie=True,
                    yAxis_array=yAxis_array)
