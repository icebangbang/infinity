import logging
from datetime import datetime, timedelta

import pandas
import pandas as pd

from app.main.db.mongo import db
from app.main.stock.dao import k_line_dao, board_dao, stock_dao
from app.main.utils import date_util, cal_util, stock_util
from app.main.utils.date_util import WorkDayIterator


def get_board_k_line_by_offset(from_date, to_date, concept_name, level='day'):
    db_name = "k_line_" + level
    my_set = db[db_name]
    board_dao.get_board_k_line_data_from_db(from_date, to_date, concept_name)
    daily_price = pd.DataFrame(board_dao.get_board_k_line_data_from_db(from_date, to_date, concept_names))

    daily_price = daily_price.set_index("date", drop=False)
    return daily_price


def publish(days=10, slice=30, code_list=None, stock_map={}, start=None, end=None):
    if start is None and end is None:
        end = date_util.get_start_of_day(datetime.now())
        start = date_util.get_work_day(end, offset=days)

    boards = board_dao.get_all_board(type=[2])

    rise = []
    result_dict = dict()
    name_dict = dict()
    for stock in boards:
        name_dict[stock['board']] = stock['board']

    page_size = 200
    start_index = 0
    end_index = page_size
    flag = False

    while flag is False:
        logging.info("current index is {}".format(start_index))
        if end_index < len(boards):
            inner = boards[start_index:end_index]
            start_index = end_index
            end_index = end_index + page_size
        else:
            inner = boards[start_index:]
            flag = True
        temp_code_list = [item['board'] for item in inner]
        result_dict = {item['board']: [] for item in inner}
        k_list = board_dao.get_board_k_line_data_from_db(start, end, temp_code_list)
        for k in k_list:
            result_dict[k['name']].append(k)
        for k, v in result_dict.items():
            if len(v) > 0:
                if len(v) == 1:
                    earliest = v[0]["open"]
                    latest = v[0]["close"]
                    c = (latest - earliest) / earliest
                else:
                    earliest = v[0]["close"]
                    latest = v[-1:][0]["close"]
                    c = (latest - earliest) / earliest
                rise.append((k, name_dict[k], c))
        result_dict.clear()

    rise = pd.DataFrame(rise)
    rise.columns = ['code', 'name', 'rise']
    rise = rise.sort_values(by='rise', ascending=False)
    new = rise.to_dict("records")

    top = new[0:slice]

    rise = rise.sort_values(by='rise', ascending=True)
    new = rise.to_dict("records")

    bot = new[0:slice]

    print("涨幅前{}是:".format(slice))
    for i in top:
        print("{} {} {} {}".format(i['code'], i['name'], i['rise'], get_concepts(stock_map, i['code'])))

    print("跌幅前{}是:".format(slice))
    for i in bot:
        print("{} {} {} {}".format(i['code'], i['name'], i['rise'], get_concepts(stock_map, i['code'])))


def get_concepts(stock_map, code):
    if code in stock_map.keys():
        return stock_map[code]['board']
    return ""


def get_all_board() -> list:
    """
    获取板块数据,包括自定义板块
    :return:
    """
    config = db['config']
    board_info = config.find_one({"name": "board"}, {"_id": 0})
    board_custom = board_info['value']

    set = db['board_detail']
    condition1 = {"board": {"$in": board_custom}}
    condition2 = {"type": 2}
    boards_custom = list(set.find(condition1, dict(board=1, _id=0, codes=1)))
    boards = list(set.find(condition2, dict(board=1, _id=0, codes=1)))
    boards_custom.extend(boards)
    return boards_custom


def get_all_board_names():
    """
    获取板块数据,包括自定义板块
    :return:
    """
    boards = get_all_board()
    results = [board['board'] for board in boards]
    return results


def get_trade_info(industry, start, end):
    """
    获取行业板块的成交信息
    :param start:
    :param end:
    :return:
    """
    return list(db['board_trade_volume']
                .find({"date": {"$gte": start, "$lte": end},
                       "industry": industry}).sort("date", 1))


def collect_trade_money(start, end):
    """
    计算交易金额和成交量
    :return:
    """
    # 板块
    collect_industry_info(start, end)
    # 大盘
    collect_index_info(start, end)
    # 省份
    collect_province_info(start, end)


def collect_industry_info_yearly(year):
    """
    计算年级别
    :param year:
    :return:
    """
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)
    boards = get_all_board()
    for board in boards:
        industry = board['board']
        codes = board['codes']
        lines = k_line_dao.get_k_line_data(start, end, codes=codes)
        df = pandas.DataFrame(lines)
        trade_stock_size =len(df.groupby("code"))
        money_sum = df['money'].sum()
        volume_sum = df['volume'].sum()
        money = cal_util.divide(money_sum, 100000000, 3)
        logging.info("同步板块{}的{}年交易量和成交额:{},{}".format(industry, year, money, volume_sum))
        update_item = dict(industry=industry, date=start,
                           volume=volume_sum, money=money, level="year",trade_stock=trade_stock_size)
        db['board_trade_volume'].update_one({"industry": industry, "date": start, "level": "year"},
                                            {"$set": update_item}, upsert=True)


def collect_industry_info(start, end):
    """
    行业板块
    :param start:
    :param end:
    :return:
    """
    boards = get_all_board()
    for board in boards:
        for date in WorkDayIterator(start, end):
            industry = board['board']
            codes = board['codes']
            lines = k_line_dao.get_k_line_data(date, date, codes=codes)
            money_sum = sum([line['money'] for line in lines])
            volume_sum = sum([line['volume'] for line in lines])
            money = cal_util.divide(money_sum, 100000000, 3)
            logging.info("同步板块{}的交易量和成交额:{},{},{}".format(industry, date, money, volume_sum))
            update_item = dict(industry=industry, date=date,
                               volume=volume_sum, money=money)
            db['board_trade_volume'].update_one({"industry": industry, "date": date},
                                                {"$set": update_item}, upsert=True)


def collect_index_info(start, end):
    """
    大盘数据
    :param start:
    :param end:
    :return:
    """
    stocks = stock_dao.get_all_stock(dict(code=1, name=1, _id=0, date=1))
    belong_map = {"创业板": [], "深市": [], "沪市": [], "科创板": []}
    for stock in stocks:
        code = stock['code']
        belong = stock_util.market_belong(code)
        belong_map[belong].append(code)
    for date in WorkDayIterator(start, end):
        for belong, codes in belong_map.items():
            lines = k_line_dao.get_k_line_data(date, date, codes=codes)
            money_sum = sum([line['money'] for line in lines])
            volume_sum = sum([line['volume'] for line in lines])
            money_sum = cal_util.divide(money_sum, 100000000, 3)
            logging.info("同步板块{}的交易量和成交额:{},{},{}".format(belong, date, volume_sum, money_sum))
            update_item = dict(industry=belong, date=date,
                               volume=volume_sum, money=money_sum)
            db['board_trade_volume'].update_one({"industry": belong, "date": date},
                                                {"$set": update_item}, upsert=True)

def collect_province_info(start, end):
    """
    以省份为维度成交额数据
    :param start:
    :param end:
    :return:
    """
    code_province_dict = stock_dao.get_code_province_map()


    stocks = stock_dao.get_all_stock(dict(code=1, name=1, _id=0, date=1))
    belong_map = {}
    for stock in stocks:
        code = stock['code']
        province = code_province_dict[code]
        belongs = belong_map.get(province,[])
        belongs.append(code)
        belong_map[province] = belongs
    for date in WorkDayIterator(start, end):
        for province, codes in belong_map.items():
            lines = k_line_dao.get_k_line_data(date, date, codes=codes)
            money_sum = sum([line['money'] for line in lines])
            volume_sum = sum([line['volume'] for line in lines])
            money_sum = cal_util.divide(money_sum, 100000000, 3)
            logging.info("同步板块{}的交易量和成交额:{},{},{}".format(province, date, volume_sum, money_sum))
            update_item = dict(industry=province, date=date,
                               volume=volume_sum, money=money_sum)
            db['board_trade_volume'].update_one({"industry": province, "date": date},
                                                {"$set": update_item}, upsert=True)

if __name__ == "__main__":
    # end = date_util.get_start_of_day(datetime.now())
    # start = end - timedelta(356)
    # collect_trade_money(start, end)
    collect_province_info(datetime(2023,1,3),datetime(2023,1,30))
    # collect_industry_info_yearly(2022)