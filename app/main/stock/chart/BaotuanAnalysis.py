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
        data_y = [data['percent'] for data in data_list]

        return dict(x=data_x, y=data_y,desc="资金集中度分析")
