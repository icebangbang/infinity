"""
同步etf数据
"""
import os
from datetime import datetime
import akshare as ak
import pandas as pd
from app.main.utils import date_util, simple_util, cal_util
import logging as log
from app.main.modules.jieba import cut_word


def test_cut(input):
    seg_list = cut_word.cut(input)  # 搜索引擎模式
    print(", ".join(seg_list))


def fetch_kline_data(code,belong):
    """
    获取场内etf交易数据
    :param code:
    :return:
    """
    df = ak.fund_etf_hist_sina(belong+code)
    # 亿级别
    df['money'] = df['volume'] * (df['high'] + df['low']) / 2 / 10000
    df['prev_close'] = df.loc[df['close'].shift(-1) > 0, 'close']
    df['prev_close'] = df['prev_close'].shift()
    df.fillna(0, inplace=True)
    df['code'] = code
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    return df.to_dict("records")


def get_etf_list():
    """
    从新浪获取etf基金
    :return:
    """
    df = ak.fund_etf_category_sina("ETF基金")
    efts = df[['代码', '名称']]
    efts = efts.rename(columns={'代码': "code", "名称": "name"})

    etfs = efts.to_dict("records")
    for etf in etfs:
        etf['belong'] = etf['code'][0:2]
        etf['code'] = etf['code'][2:]

    return etfs


def get_etf_detail(code) -> dict:
    """
    获取所有的场内etf的细节信息
    name=body['jjjc'],  # 基金简称
    code=body['symbol'],
    start_time=body['clrq'],  # 成立时间
    body=body['jjgm'],  # 体量
    company = body['glr'], #管理公司
    style = body['FinanceStyle'], #风格
    :return:
    """
    etf_basic_info = ak.fund_etf_basic_info_sina(code)

    name = etf_basic_info['name']
    name = name.replace("ETF", "")
    name_tag: list = cut_word.cut(name)
    etf_basic_info['name_tag'] = name_tag

    return etf_basic_info


def get_etf_hold(fund_code, fund_name):
    """
    获得基金持仓数据
    :return:
    """
    latest_report_day, season = date_util.get_report_day(datetime.now())
    # 重新由overwrite实现fund_portfolio_hold_em
    fund_portfolio_hold_em_df = ak.fund_portfolio_hold_em(symbol=fund_code,
                                                          date=str(latest_report_day.year))
    if fund_portfolio_hold_em_df.empty:
        return list()
    key = "{}年{}季度股票投资明细".format(latest_report_day.year, season)
    df = fund_portfolio_hold_em_df[fund_portfolio_hold_em_df['季度'] == key]

    df = df[['股票代码', '股票名称', '占净值比例', '持股数', '持仓市值']]
    df = df.rename(columns={'股票代码': "code",
                            "股票名称": "name",
                            "占净值比例": "rate",
                            "持股数": "hold_count",
                            "持仓市值": "hold_money"})
    df['update_time'] = datetime.now()
    df['season'] = season
    df['year'] = latest_report_day.year
    df['fund_code'] = fund_code
    df['fund_name'] = fund_name
    return df.to_dict("records")


if __name__ == "__main__":
    # d = get_etf_list()
    # d = get_etf_hold("510010")
    d = fetch_kline_data("510010","sh")
    print(d)
