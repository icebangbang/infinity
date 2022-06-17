import datetime
import time

import akshare as ak
import json
import pymongo
import pandas as pd
import logging as log
import requests
import akshare as ak


# concept = ak.stock_board_concept_name_ths()
# stock_sse_summary_df = ak.stock_sse_summary()
# print(stock_sse_summary_df)
from app.main.stock.dao import  stock_dao


def get_stock_list():
    log.info("开始获取上证 {} 股票".format("主板A股"))
    stock_info_sh_df = ak.stock_info_sh_name_code(indicator="主板A股")
    sh_custom_df = pd.DataFrame(stock_info_sh_df[['COMPANY_CODE', 'COMPANY_ABBR', 'LISTING_DATE']])
    sh_custom_df.columns = ['code', 'name', 'date']
    sh_custom_df['belong'] = "sh"

    stock_kc_info_sh_df = ak.stock_info_sh_name_code(indicator="科创板")
    sh_kc_custom_df = pd.DataFrame(stock_kc_info_sh_df[['COMPANY_CODE', 'COMPANY_ABBR', 'LISTING_DATE']])
    sh_kc_custom_df.columns = ['code', 'name', 'date']
    sh_kc_custom_df['belong'] = "sh"

    stock_info_sz_name_code_df = ak.stock_info_sz_name_code(indicator="A股列表")
    sz_custom_df = pd.DataFrame(stock_info_sz_name_code_df[['A股代码', 'A股简称', 'A股上市日期']])
    sz_custom_df.columns = ['code', 'name', 'date']
    sz_custom_df['belong'] = "sz"

    total = pd.concat([sh_custom_df, sh_kc_custom_df, sz_custom_df], axis=0)

    return total.to_dict(orient='records')


def get_stock_indicator(code, name):
    log.info("开始获取 {},{} 个股指标".format(code, name))
    resp = requests.get("https://stock.9fzt.com/index/sz_300763.html?from=BaiduAladdin")
    body = resp.text

def get_all_stock():
    df = ak.stock_a_lg_indicator(stock="all")
    return df.to_dict(orient='records')

def get_zt_pool():
    df = ak.stock_em_zt_pool(date='20210910')

    industry = df['所属行业'].value_counts(normalize=False, sort=True).to_frame('count').reset_index()
    industry['perc'] = industry['count'].div(len(df))
    industry.columns = ['industry','count','perc']

    return df,industry


def get_stock_web(stock):
    return ak.get_stock_web(stock)

def get_stock_business(stock):
    business = ak.get_stock_business(stock)
    zygcfx = business['zygcfx']
    df = pd.DataFrame(zygcfx)

    for REPORT_DATE, group in df.groupby("REPORT_DATE",sort=False):
        group = group[['REPORT_DATE','MAINOP_TYPE',"ITEM_NAME","MBI_RATIO"]]
        group["MBI_RATIO"] = group.apply(lambda a:
                          round(a["MBI_RATIO"]* 100,2),axis=1)
        group["REPORT_DATE"] = pd.to_datetime(df["REPORT_DATE"],format='%Y-%m-%d %H:%M:%S')
        group["REPORT_DATE"] = group["REPORT_DATE"].apply(lambda x: x.strftime("%Y-%m-%d"))

        # 获取最新的报告,所以在第一重遍历中直接返回
        return group.to_dict(orient="records")


if __name__ == "__main__":
    # get_stock_indicator("","")
    # stock_changes()
    # origin,industry = get_zt_pool()
    # get_best(origin,industry)
    print(get_stock_business(dict(code="300763",belong="sz")))