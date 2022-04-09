from backtrader.feeds import PandasData
from app.main.stock.company import Company
from app.main.stock.dao import k_line_dao
from app.main.stock.sub_startegy import SubST
from app.main.stock import constant
from app.main.stock.ind.bollinger import BollingerBandsWidth
from app.main.utils import cal_util, date_util
from datetime import datetime, timedelta

import logging


class EarningRateFeature(SubST):
    """
    未来收益率
    """

    def __init__(self, **kwargs):
        """
        :param period: 布林轨道宽度
        :param match_num:
        """
        self.day_span = [1, 2, 3, 5, 10, 15, 20]
        self.now = datetime.now()

        # self.period = period
        # self.match_num = match_num

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
        if day != 0: return  # 只考虑当日触发情况
        current = data.datetime.datetime()
        # 计算间隔时间
        days = date_util.get_days_between(self.now, current)
        if days == 0: return
        current_close = data.close[0]
        k_line_list = k_line_dao.get_k_line_by_code([company.code], current + timedelta(days=1),
                                                    end_day=current + timedelta(days=50),limit=30)

        try:
            for span in self.day_span:
                if span > len(k_line_list):
                    # company.set(constant.__dict__['earning_rate_' + str(span)], rate)
                    continue
                else:
                    k_line = k_line_list[span - 1]
                    rate = round((k_line['close'] - current_close) / current_close * 100, 2)
                    company.set(constant.__dict__['earning_rate_' + str(span)], rate)

        except Exception as e:
            logging.info(e)
