import logging

from backtrader.feeds import PandasData

from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
from app.main.utils import cal_util


class WilliamsFeature(SubST):
    """
    威廉指标相关特征。
    指导原则：波幅破位（前提：在判断大势后，再选用指标交易）
        1：上穿50，做空
        2：下穿50，做多
    """

    def __init__(self, **kwargs):
        self.periods = [6, 10]

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
            close = data.close[0]  # 当日价格
            high_record = self.high_record(data)
            low_record = self.low_record(data)

            for index, period in enumerate(self.periods):
                wr = cal_util.get_williams(high_record[index], low_record[index], close)
                company.set("wr_{}".format(period), wr)
        except Exception as e:
            logging.info(e)

    def high_record(self, data: PandasData):
        """
        近n天的最高点
        :return:
        """

        return [max(data.high.get(ago=0, size=period)) for period in self.periods]

    def low_record(self, data: PandasData):
        """
        近n天的最低点
        :return:
        """
        return [min(data.low.get(ago=0, size=period)) for period in self.periods]
