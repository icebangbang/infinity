from pandas import DataFrame

from app.main.stock.backtrade_v2.stock_holding import StockHolding


class Core:
    data: DataFrame
    holding = None
    buy_strategy = None
    sell_strategy = None

    def set_trader(self, trader):
        self.trader = trader

    def init(self, trader, **kwargs):
        holding = StockHolding(trader=trader)
        self.buy_strategy_instance = kwargs['buy_strategy'](holding)
        self.sell_strategy_instance = kwargs['sell_strategy'](holding)

        self.holding = holding
        self.__dict__.update(kwargs)

    def apply_row(self, row):
        self.buy_strategy_instance.trigger(row)
        self.sell_strategy_instance.trigger(row)
        self.holding.record_income(row)

    def run(self):
        if self.data is None: raise Exception("empty data")
        self.data.apply(lambda row: self.apply_row(row), axis=1)

    def add_data(self, data: DataFrame):
        """
        添加运行数据
        :return:
        """
        self.data: DataFrame = data