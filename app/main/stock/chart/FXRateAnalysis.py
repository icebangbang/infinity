from datetime import datetime, timedelta

from app.main.db.mongo import db
from app.main.stock.chart.Line import Line
from app.main.utils import date_util, cal_util


class FXRateAnalysis(Line):
    """
    生成线性图表
    美元对人民币汇率图表
    """

    def generate(self, **kwargs):
        rmb_fxrate = db['rmb_fxrate']
        # 获取所有数据点位
        start = datetime.now() - timedelta(days=1.5 * 375)
        data_list = list(rmb_fxrate.find({'date': {"$gte": start}}))
        # data_x = [date_util.date_time_to_str(data['date'], "%Y-%m") for data in data_list]
        data_x = [date_util.date_time_to_str(data['date'], "%Y-%m-%d") for data in data_list]
        y = [cal_util.round(data['us'] / 100, 3) for data in data_list]

        yAxis_array = [
            {
                "name": "美元对人民币",
                "type": 'value',
                "min": 6,
                "max": 7.5
            }
        ]
        data_y_array = [dict(name="汇率", y=y)]

        return dict(x=data_x,
                    xlabel=dict(
                        rotate=40,
                    ),
                    y_array=data_y_array,
                    yAxis_array=yAxis_array,
                    desc="人民币和美元汇率",
                    )
