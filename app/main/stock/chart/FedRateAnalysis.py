from datetime import datetime, timedelta

from app.main.db.mongo import db
from app.main.stock.chart.Line import Line
from app.main.utils import date_util, cal_util


class FedRateAnalysis(Line):
    """
    生成线性图表
    美国利率
    """

    def generate(self, **kwargs):
        rmb_fxrate = db['fed_interest_rate']
        # 获取所有数据点位
        start = datetime.now() - timedelta(days=80 * 375)
        data_list = list(rmb_fxrate.find({'date': {"$gte": start}}))
        # data_x = [date_util.date_time_to_str(data['date'], "%Y-%m") for data in data_list]
        data_x = [date_util.date_time_to_str(data['date'], "%Y-%m-%d") for data in data_list]
        y = [data['current'] for data in data_list]
        predict = [data['predict'] for data in data_list]

        yAxis_array = [
            {
                "name": "美国利率",
                "type": 'value',
                "min": 0,
                "max": "dataMax"
            }
        ]
        data_y_array = [dict(name="利率", y=y,yAxisIndex=0),dict(name="预期利率", y=predict,yAxisIndex=0)]

        return dict(x=data_x,
                    xlabel=dict(
                        rotate=40,
                    ),
                    y_array=data_y_array,
                    yAxis_array=yAxis_array,
                    desc="美联储利率",
                    )
