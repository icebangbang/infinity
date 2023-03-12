from datetime import datetime
from typing import List

import pandas as pd

from app.log import get_logger
from app.main.db.mongo import db
from app.main.model.recommend_etf import RecommendEtf
from app.main.stock.dao import k_line_dao, board_dao, etf_dao
from app.main.utils import date_util, cal_util

"""
资金流向分析
以东方财富大板块概念里的公司市值来界定资金规模
"""

log = get_logger(__name__)


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

    high_rate_result:List[RecommendEtf] = sorted(result, key=lambda d: sum([stock.rate for stock in d.relate_stocks]), reverse=True)

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

    # data_list = k_line_dao.get_k_line_data(start, now, sort=-1)
    # k_line_map = {}
    # for data in data_list:
    #     code = data['code']
    #     k_line_list = k_line_map.get(code, [])
    #     k_line_list.append(data)
    #     k_line_map[code] = k_line_list

    # stocks_copy = copy.deepcopy(stocks)
    # stocks_map = {stock['code']: dict(flowCapitalValue=stock['flowCapitalValue'],
    #                                   MarketValue=stock['MarketValue'])
    #               for stock in stocks}

    for base in stocks:
        update_time = base['update_time']
        code = base['code']
        name = base['name']
        log.info("[个股市值回溯]回溯{},{},{}天之内市值".format(code, name, days))
        # 获取最近的一个工作日
        latest = date_util.get_work_day(base['update_time'], 0)
        start = date_util.get_work_day(base['update_time'], days)

        data_list = k_line_dao.get_k_line_data(start, latest, codes=[base['code']], sort=-1)

        stock_data_list = []
        # 根据时间生成
        code = base['code']
        base_fcv = base['flowCapitalValue']
        base_mv = base['MarketValue']
        base_close = 0

        for data in data_list:
            date = data['date']
            # 说明是最近一天的市值,直接更新
            if len(stock_data_list) == 0:
                stock_data_list.append(dict(date=date, code=code, flowCapitalValue=base_fcv, MarketValue=base_mv))
                base_close = data['close']
            else:
                current_close = data['close']
                change_rate = 1 + (current_close - base_close) / base_close
                base_fcv = base_fcv * change_rate
                base_mv = base_mv * change_rate
                stock_data_list.append(dict(date=date, code=code, flowCapitalValue=cal_util.round(base_fcv, 4),
                                            MarketValue=cal_util.round(base_mv, 4)))
                base_close = current_close
        my_set = db['stock_value']

        for stock_data in stock_data_list:
            update_time = datetime.now()
            date = stock_data['date']
            code = stock_data['code']
            flowCapitalValue = stock_data['flowCapitalValue']
            MarketValue = stock_data['MarketValue']

            log.info("{}-{}".format(date_util.dt_to_str(date), code))
            my_set.update_one({"date": date, "code": code},
                              {"$set": dict(flowCapitalValue=flowCapitalValue,
                                            MarketValue=MarketValue,
                                            update_time=update_time)}, upsert=True)
    log.info("[个股市值回溯]回溯完成")


if __name__ == "__main__":
    # stocks = stock_dao.get_stock_detail_list(['300763'])
    # stocks = stock_dao.get_stock_detail_list()
    # backtrading_stock_value(stocks)
    # end = date_util.get_start_of_day(date_util.get_work_day(datetime.now(),0)[0])
    # start = end - timedelta(days=1)

    r = get_fund_by_board("计算机设备")
    pass
