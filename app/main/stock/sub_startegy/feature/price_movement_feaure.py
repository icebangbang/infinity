import logging

import numpy
from backtrader.feeds import PandasData

from app.main.stock import constant
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
from app.main.utils import cal_util


class PriceMovementFeature(SubST):
    """
    近n天涨幅和跌幅指标统计
    """

    def __init__(self, **kwargs):
        pass

    def init_ind(self, data: PandasData, company: Company):
        """
        初始化指标
        :return:
        """
        pass

    def next(self, data: PandasData, company: Company):
        """
        :return:
        """
        day = data.buflen() - len(data)
        if day != 0:
            return  # 只考虑当日触发情况
        try:
            self.price_movement_median(data,company)
        except Exception as e:
            logging.info(e, exc_info=1)
        self.trade_money_median(data, company)

    def price_movement_median(self,data,company):
        prev_close = data.prev_close.get(ago=0, size=len(data))
        close = data.close.get(ago=0, size=len(data))
        volume = data.volume.get(ago=0, size=len(data))

        rate_list = list(map(lambda x: self._get_rate(x[0],x[1]), zip(close, prev_close)))
        up_rate = [rate for rate in rate_list if rate >= 0]
        down_rate = [rate for rate in rate_list if rate < 0]
        up_median = numpy.median(up_rate)
        down_median = numpy.median(down_rate)
        vol_median = numpy.median(volume)

        company.set(constant.up_median, up_median)
        company.set(constant.down_median, down_median)
        company.set(constant.vol_median, vol_median)

    def trade_money_median(self,data,company):
        # 近十日成交金额中位数
        money = data.money.get(ago=-1, size=10)

        money_median = numpy.median(money)

        company.set(constant.money_median, float(money_median))

    def _get_rate(self,v2,v1):
        if v1 ==0: return 0
        return round((v2 - v1) / v1 * 100, 2)

