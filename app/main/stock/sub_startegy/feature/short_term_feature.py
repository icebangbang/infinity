from backtrader.feeds import PandasData
import backtrader as bt
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
from app.main.stock.ind.kdj import KDJ
from app.main.stock.algo import cal
from app.main.stock import constant
import logging


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

            close_5 = data.close.get(ago=0,size=5)
            if len(close_5) >0:
                close_rate_5 = round((close_5[len(close_5)-1]-close_5[0])/close_5[0]*100,2)
                company.set(constant.close_rate_5,close_rate_5)
            close_10 = data.close.get(ago=0,size=10)
            if len(close_10)>0:
                close_rate_10 = round((close_10[len(close_10) - 1] - close_10[0]) / close_10[0] * 100, 2)
                company.set(constant.close_rate_10,close_rate_10)



            close = data.close[0]  # 当日价格
            open = data.open[0]
            high = data.high[0]
            low = data.low[0]
            close_1 = data.close[-1]  # 昨日价格
            high_1 = data.high[-1]
            low_1 = data.high[-1]

            if low > high_1:
                gap = 1
            if high < low_1:
                gap = -1

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
