from datetime import datetime

import pandas as pd

from app.main.stock.chart.Line import Line
from app.main.stock.dao import stock_dao


class BoardValueAnalysis(Line):
    """
    板块市值分析
    """

    def generate(self, **kwargs):
        stocks = stock_dao.get_all_stock(dict(code=1, name=1, _id=0, date=1),
                                         filter={"date": {"$gte": datetime(2008, 1, 1)}})
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
