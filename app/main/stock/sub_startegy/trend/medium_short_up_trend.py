from backtrader.feeds import PandasData
import backtrader as bt
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
from app.main.stock.ind.kdj import KDJ
from app.main.stock.algo import cal



class MediumShortUpTrend(SubST):
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

        company.set("kdj", KDJ(data))

        company.set("close_gte_ma20", False)
        company.set("ma20[0]_gte_ma20[-1]", False)
        company.set("macd_incr", False)
        company.set("kdj_golden", False)

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
        kdj = company.get("kdj")

        K_0 = kdj.K[0]
        D_0 = kdj.D[0]
        J_0 = kdj.J[0]
        K_1 = kdj.K[-1]
        D_1 = kdj.D[-1]

        # 收盘价在20日线
        c1 = (data.close[0] >= ma20[0])
        # 20日线在抬高
        c2 = (round(ma20[0],2) >= round(ma20[-1],2))

        # macd 下跌动能减弱
        c3 = (macd.histo[0] >= macd.histo[-1])

        #kdj金叉
        c4 = (K_1 < D_1 and K_0 >= D_0)

        macd_histo_list = [macd.histo[0],macd.histo[-1],macd.histo[-2]]
        macd_histo_list.sort()
        smallest = macd_histo_list[0]

        m1,ignore = cal.get_line([macd.histo[-2],macd.histo[-1]])
        m2,ignore = cal.get_line([macd.histo[-1],macd.histo[0]])

        c5 = smallest == macd.histo[0] and m2>m1

        company.set("close_gte_ma20", c1)
        company.set("ma20[0]_gte_ma20[-1]", c2)
        company.set("macd_incr", c3 or c5)
        company.set("kdj_golden", c4)

        # 收盘价>20
        if c1 and c2 and c3 and c4:
            company.set_condition(self, True)

    def match_condition(self, comp: Company):
        """
        返回匹配情况
        :param comp:
        :return:
        """
        return comp.get(self.__class__.__name__)