from backtrader.feeds import PandasData
import backtrader as bt
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
from app.main.stock import constant
import logging

from app.main.utils import cal_util


class ShortTermFeature(SubST):
    """
        短线选股策略
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

        length = company.data_size
        # logging.info("{} length is {}".format(company.name, length))

        company.setInd("ma250", bt.indicators.SimpleMovingAverage(data, period=250)
        if length > 250 else [None])

        company.setInd("ma200", bt.indicators.SimpleMovingAverage(data, period=200)
        if length > 200 else [None])
        company.setInd("ma60", bt.indicators.SimpleMovingAverage(data, period=60)
        if length > 60 else [None])
        company.setInd("ma30", bt.indicators.SimpleMovingAverage(data, period=30)
        if length > 30 else [None])
        company.setInd("ma20", bt.indicators.SimpleMovingAverage(data, period=20)
        if length > 20 else [None])
        company.setInd("ma10", bt.indicators.SimpleMovingAverage(data, period=10)
        if length > 10 else [None])
        company.setInd("ma5", bt.indicators.SimpleMovingAverage(data, period=5)
        if length > 5 else [None])

        # company.set(self.__class__.__name__, False)

    def next(self, data: PandasData, company: Company):
        """
        n日线策略进行筛选
        :return:
        """
        day = data.buflen() - len(data)
        if day != 0: return  # 只考虑当日触发情况
        try:
            ma250 = company.getInd("ma250")
            ma200 = company.getInd("ma200")
            ma60 = company.getInd("ma60")
            ma30 = company.getInd("ma30")
            ma20 = company.getInd("ma20")
            ma10 = company.getInd("ma10")
            ma5 = company.getInd("ma5")
            gap = 0

            vol_10 = data.volume.get(ago=-1, size=10)
            vol_10_avg = sum(vol_10) / len(vol_10)

            vol_5 = data.volume.get(ago=-1, size=5)
            vol_5_avg = sum(vol_5) / len(vol_5)

            close_5 = data.close.get(ago=0, size=5)
            if len(close_5) > 0:
                close_rate_5 = round((close_5[len(close_5) - 1] - close_5[0]) / close_5[0] * 100, 2)
                company.set(constant.close_rate_5, close_rate_5)
            close_10 = data.close.get(ago=0, size=10)
            if len(close_10) > 0:
                close_rate_10 = round((close_10[len(close_10) - 1] - close_10[0]) / close_10[0] * 100, 2)
                company.set(constant.close_rate_10, close_rate_10)

            close = data.close[0]  # 当日价格
            high = data.high[0]
            low = data.low[0]
            close_1 = data.close[-1]  # 昨日价格
            high_1 = data.high[-1]
            low_1 = data.high[-1]

            if low > high_1:
                gap = 1
            if high < low_1:
                gap = -1

            self.avg_daily_increase(data, company)
            self.ma_position(data, company, ma5, ma10)
            self.high_record(data, company)

            company.set(constant.ma5, ma5[0])
            company.set(constant.ma10, ma10[0])
            company.set(constant.ma20, ma20[0])
            company.set(constant.ma30, ma30[0])
            company.set(constant.ma60, ma60[0])
            company.set(constant.ma200, ma200[0])
            company.set(constant.ma250, ma250[0])

            company.set(constant.vol_avg_10, vol_10_avg)
            company.set(constant.vol_avg_5, vol_5_avg)
            company.set(constant.volume, data.volume[0])
            company.set(constant.close, data.close[0])
            company.set(constant.rate, round((close - close_1) / close_1 * 100, 2))
            company.set(constant.gap, gap)
        except Exception as e:
            logging.info(e)
            company.set(constant.close, -1000)

    def avg_daily_increase(self, data: PandasData, company: Company):
        """
        日均涨幅
        :param data:
        :return:
        """
        # 近5日,日均涨幅
        close_neg_1 = data.close[-1]  # 前一天的收盘价格
        close_neg_6 = data.close[-6]  # 前6天的收盘价
        increase_avg_rate_5 = cal_util.get_rate(close_neg_1 - close_neg_6, close_neg_6) / 5

        close_neg_1 = data.close[-1]  # 前一天的收盘价格
        close_neg_11 = data.close[-11]  # 前11天的收盘价
        increase_avg_rate_10 = cal_util.get_rate(close_neg_1 - close_neg_11, close_neg_11) / 10

        close_neg_1 = data.close[-1]  # 前一天的收盘价格
        close_neg_21 = data.close[-21]  # 前21天的收盘价
        increase_avg_rate_20 = cal_util.get_rate(close_neg_1 - close_neg_21, close_neg_21) / 20

        company.set(constant.increase_avg_rate_5, increase_avg_rate_5)
        company.set(constant.increase_avg_rate_10, increase_avg_rate_10)
        company.set(constant.increase_avg_rate_20, increase_avg_rate_20)

    def ma_position(self, data: PandasData, company, ma5, ma10):
        """
        价位站上各类均线次数
        :return:
        """
        ma5_upon_20 = 0
        ma10_upon_20 = 0
        ma5_upon_10 = 0
        ma10_upon_10 = 0
        ma5_upon_5 = 0
        ma10_upon_5 = 0
        ma5_upon_max = 0
        ma10_upon_max = 0

        for i in range(20):
            if data.close.get(-i) > ma5.get(-i):
                ma5_upon_20 = ma5_upon_20 + 1
                if ma5_upon_max == i:
                    ma5_upon_max = ma5_upon_max + 1
                if ma10_upon_max == i:
                    ma10_upon_max = ma10_upon_max + 1

            if data.close.get(-i) > ma10.get(-i):
                ma10_upon_20 = ma10_upon_20 + 1
        for i in range(10):
            if data.close.get(-i) > ma5.get(-i):
                ma5_upon_10 = ma5_upon_10 + 1
            if data.close.get(-i) > ma10.get(-i):
                ma10_upon_10 = ma10_upon_10 + 1
        for i in range(5):
            if data.close.get(-i) > ma5.get(-i):
                ma5_upon_5 = ma5_upon_5 + 1
            if data.close.get(-i) > ma10.get(-i):
                ma10_upon_5 = ma10_upon_5 + 1

        company.set(constant.ma5_upon_20, ma5_upon_20)
        company.set(constant.ma10_upon_20, ma10_upon_20)
        company.set(constant.ma5_upon_10, ma5_upon_10)
        company.set(constant.ma10_upon_10, ma10_upon_10)
        company.set(constant.ma5_upon_5, ma5_upon_5)
        company.set(constant.ma10_upon_5, ma10_upon_5)
        company.set(constant.ma5_upon_max, ma5_upon_max)
        company.set(constant.ma10_upon_max, ma10_upon_max)

    def high_record(self, data, company):
        """
        近n天的高点 和当前价格距离高点的涨幅预估
        :return:
        """
        close = data.close[0]
        days = [5, 10, 20, 30, 60, 120, 200, 250]
        for day in days:
            highest = max(data.high.get(ago=-1, size=day))
            company.set("highest_{}".format(day), highest)

            rate = cal_util.get_rate(highest - close, close)
            company.set("close_away_from_highest_{}".format(day), rate)

    # def limiting(self,data):
    #     """
    #     近20日涨跌停表现
    #     :return:
    #     """
    #     # 最近连续触及涨停次数
    #     cont_touch_limiting_cnt = 0
    #     touch_limiting_cnt = 0
    #     for i in range(20):
    #         close = data.close[-i]
    #         close_neg_1 = data.close[-i-1]
    # rate =
