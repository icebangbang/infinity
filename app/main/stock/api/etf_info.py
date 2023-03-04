"""
同步etf数据
"""
import os

import akshare as ak
import pandas as pd
from app.main.utils import date_util
import logging as log
from app.main.modules.jieba import cut_word


def test_cut(input):
    seg_list = cut_word.cut_for_search(input)  # 搜索引擎模式
    print(", ".join(seg_list))


def fetch_kline_data(code):
    """
    获取场内etf交易数据
    :param code:
    :return:
    """
    df = ak.fund_etf_hist_sina(code)
    df['money'] = df['volume'] * (df['high'] + df['low']) / 2
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


def get_etf_detail(code)->dict:
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
    name = name.replace("ETF","")
    name_tag: list = cut_word.cut(name)
    etf_basic_info['name_tag'] = name_tag

    return etf_basic_info


if __name__ == "__main__":
    d = get_etf_list()
    print(d)
