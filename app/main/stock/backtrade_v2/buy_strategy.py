from app.main.stock.backtrade_v2.stock_holding import StockHolding
from  app.main.stock.backtrade_v2.core import Core
from app.main.stock.dao import k_line_dao


class AbstractBuyStrategy:
    core: Core= None

    def trigger(self, row, index):
        pass

    def __init__(self, core):
        self.core = core


class DefaultBuyStrategy(AbstractBuyStrategy):
    """
    默认买卖策略,梭哈买入
    """

    def trigger(self, date, index):
        # 开仓策略,例如第一天就开仓,假设直接选定股票是300763
        if (index == 0):
            code = "300763"
            point:dict = k_line_dao.get_k_line_data_point(code,date)
            price = point['close']
            self.core.add_holding(price,date,code)
