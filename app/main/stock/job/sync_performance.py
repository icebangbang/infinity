"""
同步业绩
"""
import akshare as ak
import pandas as pd

from app.main.stock.dao import stock_dao
from app.main.db.mongo import db
from app.main.utils import stock_util, date_util
import logging
from datetime import datetime, timedelta

from_datetime = datetime(2010, 1, 1)


def sync_balance():
    """
    同步资产负债表
    :return:
    """
    stocks = stock_dao.get_all_stock()
    stock_balance = db['stock_balance']
    # stock_balance.drop()
    # 获取最近一个交易日
    stock_balance.create_index([("date", -1), ("code", 1)])
    stock_balance.create_index([("code", 1)])

    for index,stock in enumerate(stocks):
        code = stock['code']
        name: str = stock['name']
        if "退" in name or "艾格" in name : continue
        logging.info("{},{}({})同步资产负债表".format(index,name, code))

        point = stock_balance.find_one({"code": code},sort=[('date', -1)])
        if point != None:
            latest_point_update_time = point['update']
            if latest_point_update_time + timedelta(days=7) >= datetime.now(): continue
            from_dt = date_util.parse_date_time(point['date'])
        else:
            from_dt = from_datetime


        belong = stock_util.basic_belong(code)
        while True:
            try:
                df = ak.stock_balance_sheet_by_report_em(from_dt, symbol=belong + code)
                break
            except Exception as e:
                logging.error(e, exc_info=1)

        df.rename(columns={
            'SECURITY_CODE': 'code',
            'SECURITY_NAME_ABBR': 'name',
            'REPORT_DATE': 'date',
        }, inplace=True)
        sort_df = df.sort_index(ascending=False)
        details = sort_df.to_dict("records")

        for detail in details:
            detail['update'] = datetime.now()
            stock_balance.update_one({"code": code, "date": detail['date']}, {"$set": detail},upsert=True)


def sync_profit():
    """
    同步利润表
    :return:
    """
    stocks = stock_dao.get_all_stock()
    stock_profit = db['stock_profit']
    # 获取最近一个交易日
    stock_profit.create_index([("date", -1), ("code", 1)])
    stock_profit.create_index([("code", 1)])

    for stock in stocks:
        code = stock['code']
        name: str = stock['name']
        if "退" in name or "艾格" in name : continue
        belong = stock_util.basic_belong(code)
        logging.info("{}({})同步利润表".format(name, code))

        point = stock_profit.find_one({"code": code}, sort=[('date', -1)])
        if point != None:
            latest_point_update_time = point['update']
            if latest_point_update_time + timedelta(days=7) >= datetime.now(): continue
            from_dt = date_util.parse_date_time(point['date'])
        else:
            from_dt = from_datetime

        while True:
            try:
                df = ak.stock_profit_sheet_by_report_em(from_dt, symbol=belong + code)
                break
            except Exception as e:
                logging.error(e, exc_info=1)

        df.rename(columns={
            'SECURITY_CODE': 'code',
            'SECURITY_NAME_ABBR': 'name',
            'REPORT_DATE': 'date',
        }, inplace=True)
        df = df.assign(update=datetime.now())
        details = df.to_dict("records")
        stock_profit.insert_many(details)


def sync_cash_flow():
    """
    同步现金流
    :return:
    """
    stocks = stock_dao.get_all_stock()
    stock_cash_flow = db['stock_cash_flow']
    # 获取最近一个交易日
    stock_cash_flow.create_index([("date", -1), ("code", 1)])
    stock_cash_flow.create_index([("code", 1)])


    for index,stock in enumerate(stocks):
        code = stock['code']
        name: str = stock['name']
        if "退" in name or "艾格" in name : continue

        logging.info("{},{}({})同步现金流表".format(index, name, code))

        point = stock_cash_flow.find_one({"code": code}, sort=[('date', -1)])
        if point != None:
            latest_point_update_time = point['update']
            if latest_point_update_time + timedelta(days=7) >= datetime.now(): continue
            from_dt = date_util.parse_date_time(point['date'])
        else:
            from_dt = from_datetime

        belong = stock_util.basic_belong(code)
        while True:
            try:
                df = ak.stock_cash_flow_sheet_by_report_em(from_dt, symbol=belong + code)
                break
            except Exception as e:
                logging.error(e, exc_info=1)

        df.rename(columns={
            'SECURITY_CODE': 'code',
            'SECURITY_NAME_ABBR': 'name',
            'REPORT_DATE': 'date',
        }, inplace=True)

        df = df.assign(update=datetime.now())

        details = df.to_dict("records")
        stock_cash_flow.insert_many(details)


def sync_analysis_indicator():
    """
    同步主要指标
    :return:
    """
    stocks = stock_dao.get_all_stock()
    stock_analysis_indicator = db['stock_analysis_indicator']
    # stock_analysis_indicator.drop()
    # 获取最近一个交易日
    stock_analysis_indicator.create_index([("date", -1), ("code", 1)])
    stock_analysis_indicator.create_index([("code", 1)])

    for index, stock in enumerate(stocks):
        code = stock['code']
        name: str = stock['name']
        if "退" in name or "艾格" in name : continue
        logging.info("{}.{}{}同步分析指标".format(index, name, code))

        point = list(stock_analysis_indicator.find({"code": code}, {"update": 1}).sort("date", -1).limit(1))
        if len(point) != 0:
            latest_point_update_time = point[0]['update']
            if latest_point_update_time + timedelta(days=7) >= datetime.now(): continue

            df = ak.stock_financial_analysis_indicator(latest_point_update_time.year, code, name)
            df['update'] = datetime.now()
            details = df.to_dict("records")
            for detail in details:
                stock_analysis_indicator.update_one({"code": code, "date": detail['date']}, {"$set": detail})
        else:
            df = ak.stock_financial_analysis_indicator(from_datetime.year, code, name)
            df['update'] = datetime.now()
            details = df.to_dict("records")
            stock_analysis_indicator.insert_many(details)


if __name__ == "__main__":
    sync_balance()
    # sync_cash_flow()
    sync_profit()
    # df = ak.stock_balance_sheet_by_report_em(from_datetime,symbol="SH603057")
    pass
