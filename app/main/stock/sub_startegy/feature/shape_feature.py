from backtrader.feeds import PandasData
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
from app.main.stock import constant
import logging


class ShapeFeature(SubST):
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
        pass

    def next(self, data: PandasData, company: Company):
        """
        存储k线特征
        :return:
        """
        day = data.buflen() - len(data)
        if day != 0: return  # 只考虑当日触发情况
        try:

            close = data.close[0]  # 当日价格
            open = data.open[0]
            high = data.high[0]
            low = data.low[0]

            up_shadow = high - max(open, close)  # 上影的长度
            down_shadow = max(open, close) - low  # 下影的长度

            entity_length = close - open  # 实体长度

            company.set(constant.up_shadow, up_shadow)
            company.set(constant.down_shadow, down_shadow)
            company.set(constant.entity_length, entity_length)


        except Exception as e:
            logging.info(e)
