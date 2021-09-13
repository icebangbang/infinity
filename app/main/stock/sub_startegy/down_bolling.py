from backtrader.feeds.pandafeed import PandasData
from app.main.stock.sub_startegy import SubST
from app.main.stock.company import Company
from app.main.stock.ind.bollinger import BollingerBands
from app.main.stock.ind.bollinger import BollingerBandsWidth
import logging


class DownBolling(SubST):
    """
    boll轨道处于下轨策略
    """
    ind_name = "down_bolling"
    hit_result = "down_bolling_hit"

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
        company.set(self.ind_name, BollingerBands(data))
        company.set(self.hit_result, False)

    def next(self, data: PandasData, comp: Company):
        """
        n日线策略进行筛选
        :return:
        """
        day = data.buflen() - len(data)
        if day >= 3: return  # 只考虑5交易日内的数据

        ind: BollingerBands = comp.get(self.ind_name)

        # 处于中轨和下轨之间
        if data.close[0] > ind.bot[0] and data.close[0] < ind.mid[0]:
            comp.set(self.hit_result, True)

    def match_condition(self, comp: Company):
        """
        返回匹配情况
        :param comp:
        :return:
        """
        return comp.get(self.hit_result)


class CloseMidBolling(SubST):
    """
    最低价靠近中轨策略
    """
    ind_name = "close_mid_bolling"
    hit_result = "close_mid_bolling_hit"

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
        company.set(self.ind_name, BollingerBands(data))
        company.set(self.hit_result, False)

    def next(self, data: PandasData, comp: Company):
        """
        n日线策略进行筛选
        :return:
        """
        day = data.buflen() - len(data)
        if day >= 1: return  # 只考虑2交易日内的数据

        ind: BollingerBands = comp.get(self.ind_name)

        # 在中轨附近
        if abs(data.low[0]- ind.mid[0]) / (ind.top[0]-ind.mid[0]) <= 0.01:
            print(abs(data.low[0]- ind.mid[0]) / (ind.top[0]-ind.mid[0]))
            comp.set(self.hit_result, True)

    def match_condition(self, comp: Company):
        """
        返回匹配情况
        :param comp:
        :return:
        """
        return comp.get(self.hit_result)

class CloseBotBolling(SubST):
    """
    最低价靠近中轨策略
    """
    ind_name = "close_bot_bolling"
    hit_result = "close_bot_bolling_hit"

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
        company.set(self.ind_name, BollingerBands(data))
        company.set(self.hit_result, False)

    def next(self, data: PandasData, comp: Company):
        """
        n日线策略进行筛选
        :return:
        """
        day = data.buflen() - len(data)
        if day >= 10: return  # 只考虑2交易日内的数据

        ind: BollingerBands = comp.get(self.ind_name)

        # 在中轨附近
        if abs(data.low[0]- ind.bot[0]) / (ind.mid[0]-ind.bot[0]) <= 0.01:
            print(abs(data.low[0]- ind.bot[0]) / (ind.mid[0]-ind.bot[0]))
            comp.set(self.hit_result, True)

    def match_condition(self, comp: Company):
        """
        返回匹配情况
        :param comp:
        :return:
        """
        return comp.get(self.hit_result)
