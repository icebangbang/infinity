from backtrader.feeds import PandasData
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
from app.main.stock import constant
from app.main.stock.ind.bollinger import BollingerBandsWidth
from app.main.utils import cal_util

import logging


class BollFeature(SubST):
    """
        k线形态特征
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
        company.setInd("boll", BollingerBandsWidth())

    def next(self, data: PandasData, company: Company):
        """
        :return:
        """
        day = data.buflen() - len(data)
        if day >= 20: return  # 只考虑当日触发情况
        try:
            boll = company.getInd("boll")
            # 布林轨道上沿的斜率
            slope, ignore = cal_util.get_line([boll.top[-1], boll.top[0]])
            company.set(constant.boll_top_slope, slope)

        except Exception as e:
            logging.info(e)
