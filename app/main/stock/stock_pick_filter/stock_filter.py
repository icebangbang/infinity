from app.main.stock.dao import board_dao, k_line_dao, stock_dao
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


def get_stock_status(base_date, offset, data_list=None, codes=None, code_name_map=None):
    """

    :param from_date: 开始时间
    :param to_date: 结束时间
    :param data_list: 数据集
    :param codes: 个股代号
    :param code_name_map: 代号名称映射
    :return:
    """

    if code_name_map is None:
        code_name_map = stock_dao.get_code_name_map()

    input = []
    if data_list is None:
        for code in codes:
            data_list = k_line_dao.get_k_line_data_by_offset(base_date, offset, code=code)
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
    code_name_map = stock_dao.get_code_name_map()
    base_date = datetime(2022, 4, 20)
    offset = -252
    now = datetime.now()

    while  base_date <= now:
        companies = get_stock_status(base_date, offset, data_list=None, codes=['300026'], code_name_map=code_name_map)
        for company in companies:
            trend_service.save_stock_trend_with_company(company, base_date)
        print(companies)
        base_date = date_util.add_and_get_work_day(base_date, 1)
    # stock_dao.dump_stock_feature(companies, to_date)

    # codes = ['600058', '600167', '600222', '600227', '600243', '600257', '600299', '600308', '600319', '600354', '600358', '600371', '600406', '600455', '600530', '600540', '600583', '600613', '600678', '600803', '600819', '600956', '600977', '601579', '603079', '603080', '603090', '603168', '603269', '603626', '603696', '603789', '603822', '603838', '603959', '603970', '603983', '603987', '000523', '000529', '000669', '000713', '000798', '000803', '000876', '000990', '000998', '002031', '002100', '002112', '002124', '002237', '002261', '002267', '002290', '002304', '002309', '002321', '002330', '002655', '002665', '002722', '002746', '002779', '002783', '002865', '003003', '300071', '300094', '300119', '300168', '300169', '300179', '300243', '300268', '300288', '300402', '300422', '300423', '300468', '300503', '300511', '300620', '300659', '300830', '300849', '300865', '300886', '300937']
    # stock_details = stock_dao.get_stock_detail_list(codes)
    # stock_map = {}
    # boards = []
    # df = pd.DataFrame(columns=['代码', '名称', '最新'])
    # for stock in stock_details:
    #     df = df.append({"代码": stock['code'], "名称": stock['name'], '最新': '--'}, ignore_index=True)
    #     # stock['code'] = stock
    #     boards.extend(stock['board'])
    #
    # # pd.DataFrame(boards).groupby(0).apply(lambda x:x.sort_values(0,ascending=False))
    #
    # pd.DataFrame(boards)[0].value_counts(normalize=False, sort=True).to_frame('count').reset_index()
    # if len(codes) != 0:
    #     stock_service.publish(10, 30, codes, stock_map)
    #
    # df.to_csv("temp.csv", sep='\t', index=False)
