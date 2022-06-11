import logging

from app.main.stock.dao import board_dao, k_line_dao
from app.main.stock.job import bt_runner
from datetime import datetime

from app.main.stock.service import board_service, stock_service, stock_index_service
from app.main.stock.strategy.strategy_wrapper import StrategyWrapper
from app.main.stock.sub_startegy.feature.boll_feature import BollFeature
from app.main.stock.sub_startegy.feature.box_type import BoxType
from app.main.stock.sub_startegy.feature.earning_rate_feature import EarningRateFeature
from app.main.stock.sub_startegy.feature.market_status_feature import MarketStatusFeature
from app.main.stock.sub_startegy.feature.price_movement_feaure import PriceMovementFeature
from app.main.stock.sub_startegy.feature.shape_feature import ShapeFeature
from app.main.stock.sub_startegy.feature.short_term_feature import ShortTermFeature
import pandas as pd

from app.main.stock.sub_startegy.feature.stock_status_feature import StockStatusFeature
from app.main.stock.sub_startegy.feature.wiliiams_feature import WilliamsFeature


def get_board_status(base_date, offset, names=None):
    """
    中长期(Medium&LongTerm)指数强弱判断
    """
    input = []
    for name in names:
        data_list = k_line_dao.get_k_line_data_by_offset(base_date, offset, table_name="board_k_line", key="name",code=name)
        input.extend(data_list)

    data_df = pd.DataFrame(input)
    data_df = data_df.set_index("date", drop=False)

    sub_st = [MarketStatusFeature, PriceMovementFeature,
              ShortTermFeature, ShapeFeature, BollFeature,
              EarningRateFeature, BoxType, WilliamsFeature]

    kwargs = {}

    companies = list()
    for name, group in data_df.groupby("name"):
        logging.info("feed {} to cerebro".format(name))

        company = bt_runner.run(base_date, offset,
                                data=group, key="code",
                                main_st=StrategyWrapper,
                                sub_st=sub_st,
                                code=name,
                                name=name, **kwargs)

        if company is not None:
            companies.append(company)
    return companies


if __name__ == "__main__":
    base_date = datetime(2022, 6, 10)
    companies = get_board_status(base_date, -252, ['船舶制造','塑料制品'])
    print(123)
