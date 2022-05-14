from app.main.stock.chart.Line import Line
from app.main.db.mongo import db
from app.main.utils import date_util


class BaotuanAnalysis(Line):
    """
    抱团分析图标
    """

    def generate(self):
        baotuan_analysis = db['baotuan_analysis']
        # 获取所有数据点位
        data_list = list(baotuan_analysis.find({}))
        data_x = [date_util.date_time_to_str(data['date'], "%Y-%m") for data in data_list]
        y = [data['percent'] for data in data_list]

        yAxis_array = [
            {
                "name": "抱团比例",
                "type": 'value'
            }
        ]
        data_y_array = [dict(name="资金集中度比例", y=y,
                             markPoint={"data": [{"type": 'max', "name": "max"}]},
                             markLine={"data": [{"type": 'average', "name": "average"}]})]

        return dict(x=data_x,
                    y_array=data_y_array,
                    yAxis_array=yAxis_array,
                    desc="a股资金集中度分析",

                    )
