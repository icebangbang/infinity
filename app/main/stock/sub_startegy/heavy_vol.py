from backtrader.feeds.pandafeed import PandasData
from app.main.stock.sub_startegy import SubST
from app.main.stock.company import Company
import backtrader as bt
import logging


class HeavyVol(SubST):
    """
    放量上涨策略
    """

    def __init__(self, period=10):
        """
        :param period: 放量对比周期周期
        :param match_num:
        """
        self.period = period

    def init_ind(self, data: PandasData, company: Company):
        """
        初始化指标
        :return:
        """

        company.set("heavy_vol_hit", False)
        company.set("heavy_vol_cond",
                    bt.And(data.volume == bt.ind.Highest(data.volume, period=self.period, plot=False)))

    def next(self, data: PandasData, comp: Company):
        """

        :return:
        """
        day = data.buflen() - len(data)
        if day >= 1: return  # 最近一天

        if comp.get("heavy_vol_cond"):
            comp.heavy_vol_hit = True
            comp.vol = data.volume[0]

    def match_condition(self, comp: Company):
        """
        返回匹配情况
        :param comp:
        :return:
        """
        return comp.heavy_vol_hit
