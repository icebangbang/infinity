from datetime import datetime

import akshare as ak
import pandas as pd
from pandas import DataFrame

from app.main.db.mongo import db
from app.main.utils import date_util


def get_stock_changes():
    pass


def dump_stock_share_change(code, start: datetime, end: datetime):
    """
    股本结构变动同步
    :return:
    """
    start: str = date_util.dt_to_str(start)
    end: str = date_util.dt_to_str(end)
    # r = ak.stock_share_change_cninfo("300763","20190101","20240101")
    result_df: DataFrame = ak.stock_share_change_cninfo(code, start, end)
    # 选取需要的列
    result_df = result_df[['变动原因', '公告日期', '变动日期', '总股本', '流通受限股份', '已流通股份', '变动原因编码']]
    # 列重命名
    result_df = result_df.rename(columns={"变动原因": "change_reason",
                                          "公告日期": "report_date",
                                          "变动日期": "change_date",
                                          "总股本": "total_capital_stock",
                                          "流通受限股份": "frozen_capital_stock",
                                          "已流通股份": "flow_capital_stock",
                                          "变动原因编码": "change_reason_code"})
    # 时间字符串格式化
    result_df['report_date'] = pd.to_datetime(result_df['report_date'], format='%Y-%m-%d')
    result_df['change_date'] = pd.to_datetime(result_df['change_date'], format='%Y-%m-%d')

    result_df['report_date'] = result_df['report_date'].astype(object).where(result_df['report_date'].notnull(), None)
    result_df['change_date'] = result_df['change_date'].astype(object).where(result_df['change_date'].notnull(), None)

    result_df['code'] = code
    # 转dict
    results = result_df.to_dict(orient="records")

    for result in results:
        code = result['code']
        change_date = result['change_date']

        db['stock_share_change'].update({"code": code, "change_date": change_date},
                                        {"$set": result}, upsert=True)


if __name__ == "__main__":
    dump_stock_share_change("300763", datetime(2019, 1, 1), datetime(2024, 1, 1))
