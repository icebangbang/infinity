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
    bolling_width = "bolling_width"

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


    def next(self, data: PandasData, comp: Company):
        """
        n日线策略进行筛选
        :return:
        """
        width = comp.bolling_width.width[0]

        logging.info("{},{},{},{},{}".format(data.datetime.date(0),width))

    def match_condition(self, comp: Company):
        """
        返回匹配情况
        :param comp:
        :return:
        """
        return True
