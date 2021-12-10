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
        logging.info("{} length is {}".format(company.name, length))

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

        ma250 = company.getInd("ma250")
        ma200 = company.getInd("ma200")
        ma60 = company.getInd("ma60")
        ma30 = company.getInd("ma30")
        ma20 = company.getInd("ma20")
        ma10 = company.getInd("ma10")
        ma5 = company.getInd("ma10")

        vol = data.volume.get(ago=-1, size=10)
        vol_avg = sum(vol) / len(vol)

        try:
            company.set(constant.ma5, ma5[0])
            company.set(constant.ma10, ma10[0])
            company.set(constant.ma20, ma20[0])
            company.set(constant.ma30, ma30[0])
            company.set(constant.ma60, ma60[0])
            company.set(constant.ma200, ma200[0])
            company.set(constant.ma250, ma250[0])
        except Exception as e:
            logging.info(e)
        company.set(constant.vol_avg_10, vol_avg)
        company.set(constant.current_vol, data.volume[0])
