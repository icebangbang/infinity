from backtrader.feeds import PandasData
from app.main.stock.sub_startegy import SubST


class SimpleSellStrategy(SubST):

    def next(self, data, comp):
        pass

    def match_condition(self, comp):
        pass

    def init_ind(self, data: PandasData, company):
        pass