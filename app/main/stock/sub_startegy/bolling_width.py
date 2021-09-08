from backtrader.feeds.pandafeed import PandasData
from app.main.stock.sub_startegy import SubST
from app.main.stock.company import Company
import backtrader as bt
from app.main.stock.ind.bollinger import BollingerBandsWidth
import logging


class BollingWidth(SubST):
    """
    均线筛选策略
    """
    bolling = "bolling"
    bolling_width = "bolling_width_ind"

    def __init__(self, period=5, match_num=5):
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
        company.set(self.bolling_width, BollingerBandsWidth())
        company.set("width_change_hit", False)


    def next(self, data: PandasData, comp: Company):
        """
        n日线策略进行筛选
        :return:
        """
        day = data.buflen() - len(data)
        if day >= 1: return  # 最近一天

        width_0 = comp.get('bolling_width_ind').width[0]
        width_loss_1 = comp.get('bolling_width_ind').width[-1]
        pct = (width_0 - width_loss_1) / width_loss_1
        if pct >= 0.25:
            comp.set("width_change_hit", True)
            comp.set("boll_width", pct)


    def match_condition(self, comp: Company):
        """
        返回匹配情况
        :param comp:
        :return:
        """
        return comp.get("width_change_hit")
