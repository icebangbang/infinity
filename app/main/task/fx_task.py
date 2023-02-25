"""
汇率相关任务
"""
import pandas as pd
import akshare as ak
from app.main.db.mongo import db
from datetime import datetime
import logging as log

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


if __name__ == "__main__":
    sync_cny_fx()
