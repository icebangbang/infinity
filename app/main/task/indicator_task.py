"""
汇率相关任务
"""
import logging as log
from datetime import datetime

import akshare as ak
import pandas as pd

from app.main.db.mongo import db


def sync_cny_fx():
    """
    同步人民币对外币汇率
    :return:
    """
    log.info("开始同步人民币对外币汇率")
    df = ak.currency_boc_safe()
    df = pd.DataFrame(df[['日期', '美元', '欧元', '日元']])
    df.columns = ['date', 'us', 'eur', 'jp']

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df['update'] = datetime.now()
    db['rmb_fxrate'].drop()
    db['rmb_fxrate'].insert_many(df.to_dict(orient="records"))


def sync_comex_gold():
    """
    同步comex黄金期货日级别数据
    :return:
    """
    df = ak.futures_foreign_hist("GC")
    result_dict = df.to_dict(orient="records")
    db['k_line_day_comex_gold'].drop()
    db['k_line_day_comex_gold'].insert_many(result_dict)


if __name__ == "__main__":
    sync_comex_gold()
    pass
