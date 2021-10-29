from backtrader.feeds import PandasData
import backtrader as bt
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
from app.main.stock.ind.kdj import KDJ
from app.main.stock.algo import cal
from app.main.stock import constant


class BaseFeature(SubST):
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
        company.setInd("ma20", bt.indicators.SimpleMovingAverage(
            data, period=20))

        company.setInd("ma10", bt.indicators.SimpleMovingAverage(
            data, period=10))
        company.setInd("macd", bt.indicators.MACDHisto(data, period_me1=12, period_me2=26, period_signal=9))
        company.setInd("kdj", KDJ(data))
        company.setInd("ma5", bt.indicators.SimpleMovingAverage(
            data, period=5))

        company.set(constant.close_gte_ma20, False)
        company.set(constant.ma20_incr, False)
        company.set(constant.kdj_golden_hit_day, -1)
        company.set(constant.macd_histo, 0)
        company.set("kdj_golden", False)

        company.set(self.__class__.__name__, False)

    def next(self, data: PandasData, company: Company):
        """
        n日线策略进行筛选
        :return:
        """
        ma20 = company.getInd("ma20")
        ma10 = company.getInd("ma10")
        macd = company.getInd("macd")
        kdj = company.getInd("kdj")

        day = data.buflen() - len(data)

        K_0 = kdj.K[0]
        D_0 = kdj.D[0]
        K_1 = kdj.K[-1]
        D_1 = kdj.D[-1]
        if K_1 < D_1 and K_0 >= D_0:
            company.set(constant.kdj_golden_hit_day, day)

        if day != 0: return  # 只考虑当日触发情况

        # 收盘价在20日线之上
        company.set(constant.close_gte_ma20, data.close[0] >= ma20[0])
        # 20日线在抬高
        company.set(constant.ma20_incr, round(ma20[0], 2) >= round(ma20[-1], 2))

        company.set(constant.macd_histo, macd.histo[0])
        # macd 下跌动能减弱
        company.set(constant.macd_histo_incr, macd.histo[0] >= macd.histo[-1])

        macd_histo_list = [macd.histo[0], macd.histo[-1], macd.histo[-2]]
        macd_histo_list.sort()
        smallest = macd_histo_list[0]
        macd_histo_smallest_3 = smallest == macd.histo[0]
        # macd柱子近3三天最小
        company.set(constant.macd_histo_smallest_3, macd_histo_smallest_3)


        m1, ignore = cal.get_line([macd.histo[-2], macd.histo[-1]])
        m2, ignore = cal.get_line([macd.histo[-1], macd.histo[0]])
        macd_histo_incr = bool(m2 > m1)
        # macd 出现上升拐点
        company.set(constant.macd_histo_rise_point, macd_histo_incr)
        company.set(constant.kdj_k_prev,K_1)
        company.set(constant.close_gte_ma10, data.close[0] >= ma10[0])
