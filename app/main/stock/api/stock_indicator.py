import akshare as ak
import json
import pymongo
import pandas as pd
import logging as log
from app.main.db.mongo import db



# concept = ak.stock_board_concept_name_ths()
# stock_sse_summary_df = ak.stock_sse_summary()
# print(stock_sse_summary_df)

def get_stock_indicator(code, name):
    log.info("开始获取 {},{} 个股指标".format(code, name))
    df = ak.stock_a_lg_indicator(stock=code)
    return df.iloc[0].to_dict()


def get_all_stock():
    df = ak.stock_a_lg_indicator(stock="all")
    return df.to_dict(orient='records')


if __name__ == "__main__":
    stocks = get_all_stock()
    for stock in stocks:
        a = get_stock_indicator(stock['code'], stock['stock_name'])

