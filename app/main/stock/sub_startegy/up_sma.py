from backtrader.feeds.pandafeed import PandasData
from app.main.stock.sub_startegy import SubST
from app.main.stock.company import Company
import backtrader as bt


class UpSma(SubST):
    """
    均线筛选策略
    """

    def __init__(self, period=5, match_num=5):
        """
        :param period: 均线周期
        :param match_num:
        """
        ind_sma_name = "ind_sma{}"
        sma_x_count = "sma{}_up_count"
        self.period = period

        self.ind_sma_name = ind_sma_name.format(period)
        self.sma_x_count = sma_x_count.format(period)
        self.match_num = match_num

    def init_ind(self, data: PandasData, company: Company):
        """
        初始化指标
        :return:
        """
        company.set(self.ind_sma_name, bt.indicators.SimpleMovingAverage(
            data, period=5))

    def next(self, data: PandasData, comp: Company):
        """
        n日线策略进行筛选
        :return:
        """
        day = data.buflen() - len(data)
        if day >= 5: return  # 只考虑5交易日内的数据

        count = comp.get(self.sma_x_count, 0)
        if data.close[0] > comp.get(self.ind_sma_name)[0]:
            count = count + 1

        comp.sma5_up_count = count

    def match_condition(self, comp: Company):
        """
        返回匹配情况
        :param comp:
        :return:
        """
        return comp.get(self.sma_x_count) >= self.match_num
