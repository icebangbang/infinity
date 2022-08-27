from app.main.stock.backtrade_v2.stock_holding import StockHolding


class AbstractSellStrategy:
    core = None
    holding: StockHolding = None


    def trigger(self,row):
        pass

    def __init__(self, holding):
        self.holding = holding


class DefaultSellStrategy(AbstractSellStrategy):


    def trigger(self,row):
        pass

