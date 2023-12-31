from datetime import datetime

import dateutil

from app.main.stock.chart.Line import Line
from app.main.stock.dao import stock_dao


class StockListedAnalysis(Line):
    """
    市场涨跌情况分析图表
    """

    def generate(self, **kwargs):
        stocks = stock_dao.get_all_stock(dict(code=1, name=1, _id=0, date=1),
                                         filter={"date": {"$gte": datetime(2008, 1, 1)}})

        stock_dict = {}
        for stock in stocks:
            date: datetime = stock['date']
            index = "{}-{}".format(date.year, date.month)
            items = stock_dict.get(index, [])
            items.append(stock)
            stock_dict[index] = items

        yAxis_array = [
            {
                "name": "每月上市数",
                "type": 'value'
            }
        ]

        data_x = []
        y = []
        date = datetime(2008, 1, 1)
        while date <= datetime.now():
            date_str = "{}-{}".format(date.year, date.month)
            data_x.append(date_str)
            y.append(len(stock_dict.get(date_str,[])))
            date = date + dateutil.relativedelta.relativedelta(months=1)


        data_y_array = [dict(name="每月上市数", y=y,
                             color="#FD0100",
                             markPoint={"data": [{"type": 'max', "name": "max"}]},
                             markLine={"data": [{"type": 'average', "name": "average"}]})]

        return dict(x=data_x,
                    y_array=data_y_array,
                    yAxis_array=yAxis_array,
                    desc="A股公司上市概览",
                    )
