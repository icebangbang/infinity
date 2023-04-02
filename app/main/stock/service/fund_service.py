from datetime import datetime
from typing import List

import pandas as pd

from app.log import get_logger
from app.main.db.mongo import db
from app.main.model.recommend_etf import RecommendEtf
from app.main.stock.dao import k_line_dao, board_dao, etf_dao, stock_dao, stock_change_dao
from app.main.utils import date_util, cal_util

"""
资金流向分析
以东方财富大板块概念里的公司市值来界定资金规模
"""

log = get_logger(__name__)


def sync_etf_kline():
    """
    同步etf基金的k线
    该方法会一次性etf基金历史时间内所有的k线数据
    如果调用方法的时候处于交易时间，将不会返回当日的盘中数据
    需要real_time去同步
    :return:
    """
    etf_dao.dump_history_kline()


def sync_etf_kline_real_time():
    """
    同步etf基金的k线
    同步相关etf基金当日的盘中数据
    如果要保证数据能够完整，需要和sync_etf_kline一起调用
    :return:
    """
    etf_dao.dump_kline_real_time()


def get_etf_kline_day(code, start, end):
    """
    获取场内etf基金的日k线数据
    :return:
    """
    return etf_dao.get_etf_kline_day(code, start, end)


def get_etf_kline_day_with_dict(code, start, end):
    """
    获取场内etf基金的日k线数据,并把结果转为dict
    {datetime:data_point}
    :return:
    """
    data_points = get_etf_kline_day(code, start, end)
    return {data_point['date']: data_point
            for data_point in data_points}


def get_fund_by_board(board_name) -> List[RecommendEtf]:
    """
    通过板块的组成个股，匹配基金的持仓股，匹配最合适的etf基金
    :return:
    """
    board_detail = board_dao.get_board_by_name(board_name)

    if board_detail is None:
        return None

    codes = board_detail['codes']
    holds = etf_dao.get_related_etf(codes)
    holds_df = pd.DataFrame(holds)

    if holds_df.empty:
        return None

    '''
    数据去重
    DataFrame.drop_duplicates(subset=None, keep=“first”, inplace=False, ignore_index=False)
    '''
    fund_list = holds_df.drop_duplicates(subset='fund_code', keep="first", inplace=False, ignore_index=False) \
        .to_dict(orient="records")
    fund_map = {fund['fund_code']: fund['fund_name'] for fund in fund_list}

    fund_stock_map = dict()
    for fund_code, group in holds_df.groupby('fund_code'):
        fund_stock_map[fund_code] = [dict(code=item['code'],
                                          name=item['name'],
                                          rate=item['rate'])
                                     for item in group.to_dict(orient="records")]

    df_count = holds_df.groupby("fund_code").size().sort_values(ascending=False)

    # 选关联个股前5的etf基金
    result: List[RecommendEtf] = [RecommendEtf(fund_name=fund_map.get(key),
                                               fund_code=key,
                                               relate_stocks=fund_stock_map.get(key)) for key, value in
                                  df_count[:5].items()]

    high_rate_result: List[RecommendEtf] = sorted(result, key=lambda d: sum([stock.rate for stock in d.relate_stocks]),
                                                  reverse=True)

    return high_rate_result


def get_by_board(start: datetime, end: datetime):
    """
    通过板块个股的市值计算板块的整个市值
    :param start: 开始时间
    :param end: 结束时间
    :return:
    """
    stock_value = db['stock_value']

    # end_time = end
    # start_time = start-timedelta(days=2)

    query_set = {"date": start}
    stock_value_earliest = list(stock_value.find(query_set))
    stock_value_earliest = {stock_value['code']: stock_value for stock_value in stock_value_earliest}

    query_set = {"date": end}
    stock_value_latest = list(stock_value.find(query_set))
    stock_value_latest = {stock_value['code']: stock_value for stock_value in stock_value_latest}

    result = {}
    boards = board_dao.get_all_board(type=[2])
    for board in boards:
        codes = board["codes"]
        fcv_sum = 0
        for code in codes:
            if code in stock_value_latest.keys() and code in stock_value_earliest.keys():
                fcv_latest = stock_value_latest[code]['flowCapitalValue']
                fcv_earliest = stock_value_earliest[code]['flowCapitalValue']
                fcv_sum = fcv_sum + fcv_latest - fcv_earliest
        result[board['board']] = fcv_sum
    return result


def get_china_overview(stock_values):
    # stocks = stock_dao.get_stock_detail_list()
    # 流动市值 flowCapitalValue
    total_fcv = 0
    # 总市值 MarketValue
    total_mv = 0
    sh_fcv = 0
    sz_fcv = 0
    sh_mv = 0
    sz_mv = 0
    cyb_fcv = 0
    cyb_mv = 0

    kcb_fcv = 0
    kcb_mv = 0
    for stock in stock_values:
        fcv = stock['flowCapitalValue']
        mv = stock['MarketValue']

        total_fcv = total_fcv + fcv
        total_mv = total_mv + mv
        if stock['belong'] == 'sh':
            sh_fcv = sh_fcv + fcv
            sh_mv = sh_mv + mv
        if stock['belong'] == 'sz':
            sz_fcv = sz_fcv + fcv
            sz_mv = sz_mv + mv
        if stock['code'].startswith("300"):
            cyb_fcv = cyb_fcv + fcv
            cyb_mv = cyb_mv + mv
        if stock['code'].startswith("688"):
            kcb_fcv = kcb_fcv + fcv
            kcb_mv = kcb_mv + mv


def get_stock_value(code, date):
    my_set = db['stock_value']
    return my_set.find_one(dict(code=code, date=date))


def backtrading_stock_value(stocks, days=1000):
    """
    根据k线回溯市值
    :return:
    """

    my_set = db['stock_value']

    for base in stocks:
        code = base['code']
        name = base['name']
        log.info("[个股市值回溯]回溯{},{},{}天之内市值".format(code, name, days))
        # 上市时间
        market_value = base['MarketValue']

        if market_value  == 0:
            log.info("个股已经退市:{}".format(name))

        # 获取最近的一个工作日
        latest = date_util.get_work_day(base['update_time'], 0)
        start = date_util.get_work_day(base['update_time'], days)

        # 查询不复权k线
        data_list = k_line_dao.get_k_line_data(start, latest, codes=[base['code']], sort=-1, adjust='')

        interval_dict = stock_change_dao.get_stock_share_change(code)

        stock_data_list = []

        for data in data_list:
            trade_date = data['date']
            close = data['close']
            for inter in interval_dict.keys():
                if trade_date not in inter:
                    continue
                result = interval_dict[inter]
                flow_capital_stock = result['flow_capital_stock']
                # frozen_capital_stock = result['frozen_capital_stock']
                total_capital_stock = result['total_capital_stock']

                flowCapitalValue = flow_capital_stock * 10000 * close
                MarketValue = total_capital_stock * 10000 * close

                stock_data_list.append(dict(date=trade_date, code=code, flowCapitalValue=flowCapitalValue,
                                            MarketValue=MarketValue))
                break



        for stock_data in stock_data_list:
            update_time = datetime.now()
            date = stock_data['date']
            code = stock_data['code']
            flowCapitalValue = stock_data['flowCapitalValue']
            MarketValue = stock_data['MarketValue']

            my_set.update_one({"date": date, "code": code},
                              {"$set": dict(flowCapitalValue=flowCapitalValue,
                                            MarketValue=MarketValue,
                                            update_time=update_time)}, upsert=True)
    log.info("[个股市值回溯]回溯完成")


if __name__ == "__main__":
    # stocks = stock_dao.get_stock_detail_list(['300763'])
    stocks = stock_dao.get_stock_detail_list()
    backtrading_stock_value(stocks)
    # end = date_util.get_start_of_day(date_util.get_work_day(datetime.now(),0)[0])
    # start = end - timedelta(days=1)

    # r = get_fund_by_board("计算机设备")
    # pass
