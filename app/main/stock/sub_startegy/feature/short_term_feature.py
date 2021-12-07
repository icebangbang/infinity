from backtrader.feeds import PandasData
import backtrader as bt
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
from app.main.stock.ind.kdj import KDJ
from app.main.stock.algo import cal
from app.main.stock import constant


class BaseFeature(SubST):
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
        company.setInd("ma250", bt.indicators.SimpleMovingAverage(data, period=250))
        company.setInd("ma200", bt.indicators.SimpleMovingAverage(data, period=200))
        company.setInd("ma60", bt.indicators.SimpleMovingAverage(data, period=60))
        company.setInd("ma30", bt.indicators.SimpleMovingAverage(data, period=30))
        company.setInd("ma20", bt.indicators.SimpleMovingAverage(data, period=20))
        company.setInd("ma10", bt.indicators.SimpleMovingAverage(data, period=10))
        company.setInd("ma5", bt.indicators.SimpleMovingAverage(data, period=5))



        company.set(self.__class__.__name__, False)

    def next(self, data: PandasData, company: Company):
        """
        n日线策略进行筛选
        :return:
        """
        ma250 = company.getInd("ma250")
        ma200 = company.getInd("ma200")
        ma60 = company.getInd("ma60")
        ma30 = company.getInd("ma30")
        ma20 = company.getInd("ma20")
        ma10 = company.getInd("ma10")
        ma5 = company.getInd("ma10")

        day = data.buflen() - len(data)

        if day != 0: return  # 只考虑当日触发情况

        data.vol

        company.set(constant.ma5,ma5[0])
        company.set(constant.ma10,ma10[0])
        company.set(constant.ma20,ma20[0])
        company.set(constant.ma30,ma30[0])
        company.set(constant.ma60,ma60[0])
        company.set(constant.ma200,ma200[0])
        company.set(constant.ma250,ma250[0])
