from app.main.stock.dao import board_dao, k_line_dao, stock_dao
from app.main.stock.job import bt_runner, bt_bs_runner
from datetime import datetime
import pandas as pd
import akshare as ak
import logging

from app.main.stock.service import board_service, stock_service, stock_index_service
from app.main.stock.strategy.simple_bs_strategy import SimpleBsStrategy
from app.main.stock.sub_startegy.feature.box_type import BoxType
from app.main.stock.sub_startegy.feature.box_boundary import BoxBoundary
from app.main.stock.sub_startegy.feature.volume import VolumeSubST
from app.main.stock.sub_startegy.up_sma import UpSma
from app.main.stock.sub_startegy.feature.base_feature import BaseFeature



def do_trade(from_date, to_date):
    """
    发起交易
    """
    data_list = pd.DataFrame(k_line_dao.get_k_line_by_code(["688580"], from_date, to_date))

    sub_st = [BoxBoundary,BoxType,BaseFeature]

    code_name_map = stock_dao.get_code_name_map()
    companies = list()
    count = 1
    for code, group in data_list.groupby("code"):
        logging.info("feed {} to cerebro,index {}".format(code, count))
        if code in code_name_map.keys():
            name = code_name_map[code]
        else:
            name = 'no'
        company = bt_runner.run(from_date, to_date,
                                   main_st = SimpleBsStrategy,
                                   data=group,
                                   sub_st=sub_st,
                                   code=code,
                                   name=name)

        if company is not None:
            companies.append(company)
        count = count + 1

    return companies


if __name__ == "__main__":
    from_date = datetime(2020, 3, 1)
    to_date = datetime(2021, 11, 1)
    companies = do_trade(from_date, to_date)
    stock_dao.dump_stock_feature(companies, to_date)


