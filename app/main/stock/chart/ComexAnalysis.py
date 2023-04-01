from datetime import datetime, timedelta

from app.main.db.mongo import db
from app.main.stock.chart.Line import Line
from app.main.utils import date_util


class ComexAnalysis(Line):
    """
    comex黄金指标
    """

    def generate(self, **kwargs):
        comex_gold = db['k_line_day_comex_gold']
        # 获取所有数据点位
        start = datetime.now() - timedelta(days=3 * 365)
        data_list = list(comex_gold.find({'date': {"$gte": start}}))
        # data_x = [date_util.date_time_to_str(data['date'], "%Y-%m") for data in data_list]

        data_x = []
        data_y = []
        volumes = []

        for index, data in enumerate(data_list):
            # x轴，日期数据
            data_x.append(date_util.date_time_to_str(data['date'], "%Y-%m-%d"))
            # k线y轴相关数据
            data_y.append([data['open'], data['close'], data['low'], data['high'], data['volume']])

            # 交易量
            if index == 0:
                volumes.append([index, data['volume'], 1])
            else:
                volumes.append([index, data['volume'],
                                1 if data_list[index]['volume'] > data_list[index - 1]['volume'] else -1])

        # y = [cal_util.round(data['us'] / 100, 3) for data in data_list]

        # yAxis_array = [
        #     {
        #         "name": "美元对人民币",
        #         "type": 'value',
        #         "min": 6,
        #         "max": 7.5
        #     }
        # ]
        # data_y_array = [dict(name="汇率", y=y)]

        return dict(
                    xlabel=dict(
                        rotate=40,
                    ),
                    categoryData=data_x,
                    values=data_y,
                    volumes=volumes,
                    # 前端用来判断主要指标
                    desc="main",
                    )
