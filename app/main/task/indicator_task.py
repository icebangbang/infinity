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
    records = df.to_dict(orient="records")

    for record in records:
        db['rmb_fxrate'].update_one({"date":record['date']},{"$set":record},upsert=True)

    db['indicator_sync_record'].update_one({"name": "rmb_fxrate"}, {"$set": {"update_time": datetime.now()}},
                                           upsert=True)
    log.info("开始同步人民币对外币汇率同步完成,同步条数:{}".format(len(records)))


def sync_comex_gold():
    """
    同步comex黄金期货日级别数据
    :return:
    """
    df = ak.futures_foreign_hist("GC")
    result_dict = df.to_dict(orient="records")

    for result in result_dict:
        db['k_line_day_comex_gold'].update_one({"date":result['date']},{"$set":result},upsert=True)
    # db['k_line_day_comex_gold'].insert_many(result_dict)
    db['indicator_sync_record'].update_one({"name": "comex_gold"}, {"$set": {"update_time": datetime.now()}}, upsert=True)


def sync_fed_interest_rate():
    """
    同步美联储利率决议报告
    :return:
    """
    macro_bank_usa_interest_rate_df = ak.macro_bank_usa_interest_rate()
    df = macro_bank_usa_interest_rate_df[['日期', '今值', '预测值', '前值']]

    df = df.rename(columns={
        '日期': 'date',
        '今值': 'current',
        '预测值': 'predict',
        '前值': 'prev'
    })
    df["date"] = pd.to_datetime(df["date"])
    result_dict_list = df.to_dict(orient="records")

    db['fed_interest_rate'].drop()
    db['fed_interest_rate'].insert_many(result_dict_list)

    for result_dict in result_dict_list:

        db['calendar_event'].update_one({"title": "美联储利率决议",
                                         "start": result_dict['date']},
                                        {"$set": dict(source="美联储",start=result_dict['date'],title="美联储利率决议")},
                                        upsert=True)


if __name__ == "__main__":
    sync_comex_gold()
    # sync_cny_fx()
    pass
