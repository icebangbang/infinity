from app.main.stock.dao import stock_dao, k_line_dao, board_dao
from datetime import datetime, timedelta
import copy
from app.main.db.mongo import db
import logging

from app.main.utils import date_util

"""
资金流向分析
以东方财富大板块概念里的公司市值来界定资金规模
"""

"""
获取a股整体市值
"""


def get_by_board(start: datetime, end: datetime):
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


def backtrading_stock_value(stocks, days=90):
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
        logging.info("start backtrading stock value,days is {}".format(days))
        latest, update_time = date_util.get_work_day(base['update_time'], 0)
        start = latest - timedelta(days=days)

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
                stock_data_list.append(dict(date=date, code=code, flowCapitalValue=round(base_fcv, 4),
                                            MarketValue=round(base_mv, 4)))
                base_close = current_close
        my_set = db['stock_value']

        for stock_data in stock_data_list:
            update_time = datetime.now()
            date = stock_data['date']
            code = stock_data['code']
            flowCapitalValue = stock_data['flowCapitalValue']
            MarketValue = stock_data['MarketValue']

            logging.info("{}-{}".format(date_util.dt_to_str(date), code))
            my_set.update_one({"date": date, "code": code},
                              {"$set": dict(flowCapitalValue=flowCapitalValue,
                                            MarketValue=MarketValue,
                                            update_time=update_time)}, upsert=True)
    logging.info("finish backtrading stock value")


if __name__ == "__main__":
    stocks = stock_dao.get_stock_detail_list(['300763'])
    backtrading_stock_value(stocks, 4)
    # end = date_util.get_start_of_day(date_util.get_work_day(datetime.now(),0)[0])
    # start = end - timedelta(days=1)

    # results = get_by_board(start, end)
    # pass
