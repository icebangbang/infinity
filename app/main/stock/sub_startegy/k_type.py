import logging

from backtrader.feeds import PandasData

from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST


class DojiType(SubST):
    """
    十字星形态
    """

    def __init__(self, **kwargs):
        """
        :param period: 均线周期
        :param match_num:
        """
        self.period = kwargs.get("doji_appear_period", 1)

    def init_ind(self, data: PandasData, company: Company):
        """
        初始化指标
        :return:
        """
        company.set("doji_appear", False)

    def next(self, data: PandasData, company: Company):
        """
        n日线策略进行筛选
        :return:
        """
        day = data.buflen() - len(data)
        if day >= self.period - 1: return  # 只考虑5交易日内的数据

        open = data.open[0]
        close = data.close[0]

        dis = abs(open - close)
        percent = dis / open

        if percent <= 0.01:
            company.set("doji_appear", True)

    def match_condition(self, comp: Company):
        """
        返回匹配情况
        :param comp:
        :return:
        """
        return comp.doji_appear
