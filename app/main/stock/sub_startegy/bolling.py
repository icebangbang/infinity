from backtrader.feeds.pandafeed import PandasData
from app.main.stock.sub_startegy import SubST
from app.main.stock.company import Company
from app.main.stock.ind.bollinger import BollingerBands
from app.main.stock.ind.bollinger import BollingerBandsWidth
import logging


class BollingFeatures(SubST):
    """
    boll轨道下轨到上柜策略
    """
    ind_name = "down_bolling"
    hit_result = "down_bolling_hit"

    def __init__(self, **kwargs: dict):
        """
        :param period: 布林轨道宽度
        :param match_num:
        """
        pass

    def init_ind(self, data: PandasData, company: Company):
        """
        初始化指标
        :return:
        """
        company.setInd(self.ind_name, BollingerBands(data))

    def next(self, data: PandasData, comp: Company):
        """
        n日线策略进行筛选
        :return:
        """
        day = data.buflen() - len(data)
        if day >= self.period: return  # 只考虑5交易日内的数据

        ind: BollingerBands = comp.get(self.ind_name)

        # 处于中轨和下轨之间
        if data.close[-1] > ind.bot[-1] and data.close[-1] <= ind.mid[-1]:
            if data.close[0] < ind.top[0] and data.close[0] >= ind.mid[0]:
                print(ind.bot.array)
                print(ind.mid.array)
                comp.set(self.hit_result, True)

    def match_condition(self, comp: Company):
        """
        返回匹配情况
        :param comp:
        :return:
        """
        return comp.get(self.hit_result)
