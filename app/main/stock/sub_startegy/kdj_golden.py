from backtrader.feeds.pandafeed import PandasData
from app.main.stock.sub_startegy import SubST
from app.main.stock.company import Company
import backtrader as bt
from app.main.stock.ind.kdj import KDJ
import logging


class KdjGolden(SubST):
    """
    kdj金叉策略
    """
    ind_name = "kdj_golden"

    def __init__(self, period=5, match_num=5,limit=30):
        """
        :param period: 均线周期
        :param match_num:
        """
        self.period = period
        self.match_num = match_num
        self.limit = limit

    def init_ind(self, data: PandasData, company: Company):
        """
        初始化指标
        :return:
        """

        company.set(self.ind_name, KDJ(data))
        company.set("kdj_hit", False)

    def next(self, data: PandasData, comp: Company):
        """
        n日线策略进行筛选
        :return:
        """
        logging.info(data.datetime.date(0))
        day = data.buflen() - len(data)
        if day >= 3: return  # 只考虑5交易日内的数据

        kdj = comp.get(self.ind_name)
        K_0 = kdj.K[0]
        D_0 = kdj.D[0]
        J_0 = kdj.J[0]
        K_1 = kdj.K[-1]
        D_1 = kdj.D[-1]

        if K_1 < D_1 and K_0 >= D_0 and K_0 < self.limit:
            comp.kdj_hit = True
            comp.k = K_0
            comp.d = D_0
            comp.j = J_0

    def match_condition(self, comp: Company):
        """
        返回匹配情况
        :param comp:
        :return:
        """
        return comp.kdj_hit
