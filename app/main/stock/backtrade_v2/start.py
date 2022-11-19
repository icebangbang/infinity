from datetime import datetime, timedelta

from pandas import DataFrame

from app.main.stock.backtrade_v2.core import Core
from app.main.stock.backtrade_v2.stock_holding import Trader
from app.main.stock.dao import k_line_dao
from app.main.utils import date_util

if __name__ == "__main__":
    from app.main.stock.backtrade_v2.buy_strategy import DefaultBuyStrategy

    from app.main.stock.backtrade_v2.sell_strategy import DefaultSellStrategy

    # 金额，手续费，滑点
    trader = Trader(100000, 0.0001, 0.005)

    base_date = date_util.get_start_of_day(datetime.now())
    # base_date = datetime(2022,9,1)
    offset = 252
    start = base_date - timedelta(offset)
    end = datetime.now()
    # data_list = k_line_dao.get_k_line_data_by_offset(base_date, offset, code=code)
    core = Core()
    core.init(trader=trader,
              buy_strategy=DefaultBuyStrategy,
              sell_strategy=DefaultSellStrategy,
              start=start,
              end=end)
    core.run()

    # income = core.holding.income_record[-1]
    pass
