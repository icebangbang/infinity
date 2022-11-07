from app.main.stock.backtrade_v2.stock_holding import StockHolding


class AbstractPickStrategy:
    core = None
    holding: StockHolding = None


    def trigger(self,row):
        pass

    def __init__(self, holding,core):
        self.holding = holding
        self.core = core

class TrendPickStrategy(AbstractPickStrategy):
    pass