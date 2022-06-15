from app.main.stock.chart.Line import Line
from app.main.db.mongo import db
from app.main.stock.dao import stock_dao
from app.main.utils import date_util
from datetime import datetime
import pandas as pd

class StockListedAnalysis(Line):
    """
    市场涨跌情况分析图表
    """

    def generate(self,**kwargs):

        stocks = stock_dao.get_all_stock(dict(code=1, name=1, _id=0,date=1),
                                         filter={"date":{"$gte":"2008-01-01"}})
        # 获取所有数据点位
        df = pd.DataFrame(stocks)
        df.index = pd.to_datetime(df.date)

        r = {"{}-{}".format(dt[0], dt[1]): len(group) for dt, group in df.groupby([df.index.year, df.index.month])}

        yAxis_array = [
            {
                "name": "每月上市数",
                "type": 'value'
            }
        ]

        data_x = list(r.keys())
        y = list(r.values())
        data_y_array = [dict(name="每月上市数", y=y,
                             color="#FD0100",
                             markPoint={"data": [{"type": 'max', "name": "max"}]},
                             markLine={"data": [{"type": 'average', "name": "average"}]})]

        return dict(x=data_x,
                    y_array=data_y_array,
                    yAxis_array=yAxis_array,
                    desc="A股公司上市概览",
                    )