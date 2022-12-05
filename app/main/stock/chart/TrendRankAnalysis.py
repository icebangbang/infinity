from app.main.stock.chart.Line import Line
from app.main.db.mongo import db
from app.main.utils import date_util, cal_util
from datetime import datetime


class TrendRankAnalysis(Line):
    """
    趋势排名分析
    """

    def generate(self, **kwargs):
        dt_str = kwargs['date']
        trend = kwargs.get("trend","up")

        trend_data = db['trend_data']

        trend_data_list = list(trend_data.find({"date":date_util.parse_date_time(dt_str),"trend":trend}))

        y = [trend['industry'] for trend in trend_data_list]
        x = [ cal_util.round(trend['rate'] * 100,2) for trend in trend_data_list]

        return dict(x=x,y=y)
