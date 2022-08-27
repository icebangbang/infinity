from pandas import DataFrame

from app.main.stock.backtrade_v2.core import Core
from app.main.stock.backtrade_v2.stock_holding import Trader
from app.main.stock.dao import k_line_dao
from datetime import datetime





if __name__ == "__main__":
    from app.main.stock.backtrade_v2.buy_strategy import DefaultBuyStrategy

    from app.main.stock.backtrade_v2.sell_strategy import DefaultSellStrategy

    trader = Trader(100000, 0.0001, 0.005)

    base_date = datetime.now()
    offset = -252
    code = "300763"
    data_list = k_line_dao.get_k_line_data_by_offset(base_date, offset, code=code)
    core = Core()
    core.init(trader=trader, data=DataFrame(data_list),
              buy_strategy=DefaultBuyStrategy,
              sell_strategy=DefaultSellStrategy)
    core.run()

    income = core.holding.income_record[-1]
    pass
