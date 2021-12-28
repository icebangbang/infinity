import logging

from app.main.stock.dao import board_dao
from app.main.stock.job import bt_runner
from datetime import datetime

from app.main.stock.service import board_service, stock_service, stock_index_service
from app.main.stock.strategy.strategy_wrapper import StrategyWrapper
from app.main.stock.sub_startegy.feature.shape_feature import ShapeFeature
from app.main.stock.sub_startegy.feature.short_term_feature import ShortTermFeature
from app.main.stock.sub_startegy.up_sma import UpSma


def get_board_status(from_date, to_date, names=None):
    """
    中长期(Medium&LongTerm)指数强弱判断
    """

    data_list = board_service.get_board_k_line(from_date, to_date, names)
    # data = data[data['type']==3]
    # data = data.set_index("date", drop=False)

    sub_st = [ShortTermFeature, ShapeFeature]
    kwargs = {}

    companies = list()
    for name, group in data_list.groupby("name"):
        logging.info("feed {} to cerebro".format(name))

        company = bt_runner.run(from_date, to_date,
                                data=group, key="code",
                                main_st=StrategyWrapper,
                                sub_st=sub_st,
                                code=name,
                                name=name, **kwargs)

        if company is not None:
            companies.append(company)
    return companies


if __name__ == "__main__":
    from_date = datetime(2021, 3, 1)
    to_date = datetime(2021, 9, 14)
    companies = get_board_status(from_date, to_date, None)
    print(123)
