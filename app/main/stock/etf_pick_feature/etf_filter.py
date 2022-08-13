from app.main.stock.dao import board_dao, k_line_dao, stock_dao, etf_dao
from app.main.stock.job import bt_runner
from datetime import datetime, timedelta
import pandas as pd
import logging
import time

from app.main.stock.service import trend_service
from app.main.stock.sub_startegy.feature.box_type import BoxType
from app.main.stock.sub_startegy.feature.box_boundary import BoxBoundary
from app.main.stock.sub_startegy.feature.earning_rate_feature import EarningRateFeature
from app.main.stock.sub_startegy.feature.market_status_feature import MarketStatusFeature
from app.main.stock.sub_startegy.feature.stock_status_feature import StockStatusFeature
from app.main.stock.sub_startegy.feature.price_movement_feaure import PriceMovementFeature
from app.main.stock.sub_startegy.feature.short_term_feature import ShortTermFeature
from app.main.stock.sub_startegy.feature.shape_feature import ShapeFeature
from app.main.stock.sub_startegy.feature.boll_feature import BollFeature
from app.main.stock.strategy.strategy_wrapper import StrategyWrapper
from app.main.stock.sub_startegy.feature.wiliiams_feature import WilliamsFeature
from app.main.utils import date_util

"""
跑批获取特征
"""


def get_etf_status(base_date, offset, data_list=None, codes=None, code_name_map=None):
    """

    :param from_date: 开始时间
    :param to_date: 结束时间
    :param data_list: 数据集
    :param codes: 个股代号
    :param code_name_map: 代号名称映射
    :return:
    """

    if code_name_map is None:
        code_name_map = etf_dao.get_code_name_map()

    input = []
    if data_list is None:
        for code in codes:
            data_list = k_line_dao.get_k_line_data_by_offset(base_date, offset,
                                                             code=code,level='day',
                                                             table_name='etf_kline')
            if len(data_list) == 0:
                logging.info("datas from {} offset {} of {} is empty".format(
                    date_util.dt_to_str(base_date),
                    offset,
                    code
                ))
                continue
            input.extend(data_list)
    else:
        input = data_list
        # print(len(data_list),codes)
    # data = data.set_index("date", drop=False)

    data_df = pd.DataFrame(input)
    data_df = data_df.set_index("date", drop=False)

    sub_st = [StockStatusFeature, MarketStatusFeature, PriceMovementFeature,
              ShortTermFeature, ShapeFeature, BollFeature,
              EarningRateFeature, BoxType, WilliamsFeature]
    # sub_st = [BoxType]
    kwargs = {}

    companies = list()
    for code, group in data_df.groupby("code"):
        logging.info("feed {} to cerebro: {}, size: {}".format(code, date_util.dt_to_str(base_date), len(group)))
        if code in code_name_map.keys():
            name = code_name_map[code]
        else:
            name = 'no'

        company = None
        try:
            company = bt_runner.run(base_date, offset,
                                    data=group, key="code",
                                    main_st=StrategyWrapper,
                                    sub_st=sub_st,
                                    code=code,
                                    name=name, **kwargs)
        except Exception as e:
            logging.error("error from {} offset {} of {}".format(
                date_util.dt_to_str(base_date),
                offset,
                code
            ))
            logging.error(e, exc_info=1)

        if company is not None:
            companies.append(company)

    return companies


if __name__ == "__main__":
    code_name_map = etf_dao.get_code_name_map()
    base_date = datetime(2022, 4, 1)
    offset = -252
    now = datetime.now()

    while  base_date <= now:
        companies = get_etf_status(base_date, offset, data_list=None, codes=['sh510050'], code_name_map=code_name_map)
        # for company in companies:
        #     trend_service.save_stock_trend_with_company(company, base_date)
        print(companies)
        base_date = date_util.add_and_get_work_day(base_date, 1)



