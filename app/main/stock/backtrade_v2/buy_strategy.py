from app.main.stock.backtrade_v2.stock_holding import StockHolding


class AbstractBuyStrategy:
    core = None
    holding: StockHolding = None

    def trigger(self, row):
        pass

    def __init__(self, holding):
        self.holding = holding


class DefaultBuyStrategy(AbstractBuyStrategy):
    """
    默认买卖策略,梭哈买入
    """

    def trigger(self, row):
        if len(self.holding.trade_history) > 0:
            # 已有持仓,直接跳过
            pass
        else:
            self.holding.buy(row,"梭哈")


