from backtrader.feeds import PandasData

from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
import backtrader as bt
from app.main.stock.algo import cal
from app.main.stock import constant


class MediumLongTerm(SubST):
    """
        最低价靠近中轨策略
        """

    def __init__(self, **kwargs):
        """
        :param period: 布林轨道宽度
        :param match_num:
        """
        pass

        # self.period = period
        # self.match_num = match_num

    def init_ind(self, data: PandasData, company: Company):
        """
        初始化指标
        :return:
        """
        company.set("ma60", bt.indicators.SimpleMovingAverage(
            data, period=60))
        company.set("macd", bt.indicators.MACDHisto(
            data, period_me1=12, period_me2=26, period_signal=9))

        company.set(constant.close_gte_ma20, False)
        company.set(constant.ma60_incr, False)
        company.set(constant.dif_gt_0, False)
        company.set(self.__class__.__name__, False)

    def next(self, data: PandasData, company: Company):
        """
        n日线策略进行筛选
        :return:
        """
        day = data.buflen() - len(data)
        if day != 0: return  # 只考虑当日触发情况

        ma60 = company.get("ma60")
        macd = company.get("macd")

        c1 = data.close[0] >= ma60[0]
        c2 = ma60[0] >= ma60[-1]
        c3 = macd[0] > 0

        company.set("close_gte_ma60", c1)
        company.set("ma60[0]_gte_ma60[-1]", c2)
        company.set("dif>0", c3)

        # 收盘价>60
        if c1 and c2 and c3:
            company.set(self.__class__.__name__, True)

    def match_condition(self, comp: Company):
        """
        返回匹配情况
        :param comp:
        :return:
        """
        return comp.get(self.__class__.__name__)


class MediumShortTerm(SubST):
    """
        中短期上升策略
        """

    def __init__(self, **kwargs):
        """
        :param period: 布林轨道宽度
        :param match_num:
        """
        pass

        # self.period = period
        # self.match_num = match_num

    def init_ind(self, data: PandasData, company: Company):
        """
        初始化指标
        :return:
        """
        company.set("ma20", bt.indicators.SimpleMovingAverage(
            data, period=20))
        company.set("macd", bt.indicators.MACDHisto(
            data, period_me1=12, period_me2=26, period_signal=9))

        company.set("close_gte_ma20", False)
        company.set("ma20[0]_gte_ma20[-1]", False)
        company.set("dif>0", False)
        company.set("dif[-1]<0", False)

        company.set(self.__class__.__name__, False)

    def next(self, data: PandasData, company: Company):
        """
        n日线策略进行筛选
        :return:
        """
        day = data.buflen() - len(data)
        if day != 0: return  # 只考虑当日触发情况

        ma20 = company.get("ma20")
        macd = company.get("macd")

        # cal.predict()

        c1 = data.close[0] >= ma20[0]
        c2 = ma20[0] >= ma20[-1]
        c3 = macd[0] > 0
        c4 = macd[-1] <0

        company.set("close_gte_ma20", c1)
        company.set("ma20[0]_gte_ma20[-1]", c2)
        company.set("dif>0", c3)
        company.set("dif[-1]<0", c4)

        # 收盘价>20
        if c1 and c2 and c3 and c4:
            company.set(self.__class__.__name__, True)

    def match_condition(self, comp: Company):
        """
        返回匹配情况
        :param comp:
        :return:
        """
        return comp.get(self.__class__.__name__)
