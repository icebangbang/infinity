"""
同步业绩
"""
import akshare as ak

from app.main.stock.dao import stock_dao
from app.main.db.mongo import db
from app.main.utils import stock_util
import logging
from datetime import datetime

from_datetime = datetime(2010,1,1)

def sync_balance():
    """
    同步资产负债表
    :return:
    """
    stocks = stock_dao.get_all_stock()
    stock_balance = db['stock_balance']
    stock_balance.drop()
    # 获取最近一个交易日
    stock_balance.create_index([("date", -1), ("code", 1)])
    stock_balance.create_index([("code", 1)])

    for stock in stocks:
        code = stock['code']
        name:str = stock['name']
        if "退市" in name: continue
        belong = stock_util.basic_belong(code)
        logging.info("{}({})同步资产负债表".format(name,code))
        df = ak.stock_balance_sheet_by_report_em(from_datetime,symbol=belong+code)
        df.rename(columns={
            'SECURITY_CODE': 'code',
            'SECURITY_NAME_ABBR': 'name',
            'REPORT_DATE': 'date',
        }, inplace=True)
        details = df.to_dict("records")
        stock_balance.insert_many(details)



def sync_profit():
    """
    同步利润表
    :return:
    """
    stocks = stock_dao.get_all_stock()
    stock_profit = db['stock_profit']
    stock_profit.drop()
    # 获取最近一个交易日
    stock_profit.create_index([("date", -1), ("code", 1)])
    stock_profit.create_index([("code", 1)])

    for stock in stocks:
        code = stock['code']
        name: str = stock['name']
        if "退市" in name: continue
        belong = stock_util.basic_belong(code)
        logging.info("{}({})同步利润表".format(name,code))

        df = ak.stock_profit_sheet_by_report_em(from_datetime,symbol=belong + code)
        df.rename(columns={
            'SECURITY_CODE': 'code',
            'SECURITY_NAME_ABBR': 'name',
            'REPORT_DATE': 'date',
        }, inplace=True)
        details = df.to_dict("records")
        stock_profit.insert_many(details)

def sync_cash_flow():
    """
    同步现金流
    :return:
    """
    stocks = stock_dao.get_all_stock()
    stock_cash_flow = db['stock_cash_flow']
    stock_cash_flow.drop()
    # 获取最近一个交易日
    stock_cash_flow.create_index([("date", -1), ("code", 1)])
    stock_cash_flow.create_index([("code", 1)])

    for stock in stocks:
        code = stock['code']
        name: str = stock['name']
        if "退市" in name: continue
        belong = stock_util.basic_belong(code)
        logging.info("{}{}同步现金流表".format(name,code))
        df = ak.stock_cash_flow_sheet_by_report_em(from_datetime,symbol=belong + code)
        df.rename(columns={
            'SECURITY_CODE': 'code',
            'SECURITY_NAME_ABBR': 'name',
            'REPORT_DATE': 'date',
        }, inplace=True)
        details = df.to_dict("records")
        stock_cash_flow.insert_many(details)

def sync_analysis_indicator():
    """
    同步主要指标
    :return:
    """
    stocks = stock_dao.get_all_stock()
    stock_analysis_indicator = db['stock_analysis_indicator']
    stock_analysis_indicator.drop()
    # 获取最近一个交易日
    stock_analysis_indicator.create_index([("date", -1), ("code", 1)])
    stock_analysis_indicator.create_index([("code", 1)])

    for stock in stocks:
        code = stock['code']
        name: str = stock['name']
        if "退市" in name: continue
        logging.info("{}{}同步分析指标".format(name,code))
        df = ak.stock_financial_analysis_indicator(from_datetime.year,code,name)
        details = df.to_dict("records")
        stock_analysis_indicator.insert_many(details)

if __name__ == "__main__":
    # sync_cash_flow()
    sync_analysis_indicator()
    # df = ak.stock_balance_sheet_by_report_em(from_datetime,symbol="SH603057")
    pass
