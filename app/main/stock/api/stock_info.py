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
    sh_custom_df = pd.DataFrame(stock_info_sh_df[['证券代码', '证券简称', '上市日期']])
    sh_custom_df.columns = ['code', 'name', 'date']
    sh_custom_df['belong'] = "sh"

    stock_kc_info_sh_df = ak.stock_info_sh_name_code(indicator="科创板")
    sh_kc_custom_df = pd.DataFrame(stock_kc_info_sh_df[['证券代码', '证券简称', '上市日期']])
    sh_kc_custom_df.columns = ['code', 'name', 'date']
    sh_kc_custom_df['belong'] = "sh"

    stock_info_sz_name_code_df = ak.stock_info_sz_name_code(indicator="A股列表")
    sz_custom_df = pd.DataFrame(stock_info_sz_name_code_df[['A股代码', 'A股简称', 'A股上市日期']])
    sz_custom_df.columns = ['code', 'name', 'date']
    sz_custom_df['belong'] = "sz"

    total = pd.concat([sh_custom_df, sh_kc_custom_df, sz_custom_df], axis=0)
    total['date'] = pd.to_datetime(total['date'])
    return total.to_dict(orient='records')



def get_all_stock():
    df = ak.stock_a_lg_indicator(stock="all")
    return df.to_dict(orient='records')



def get_stock_web(stock):
    """
    从东财的个股详情页获取个股的官网，首次开发的需求是为了想从官网获取上市公司的经营范围
    get_stock_web 自定义编写，伪装为akshare的方法
    :param stock:
    :return:
    """
    return ak.get_stock_web(stock)

def get_stock_register_address(stock:dict):
    """
    从东财的详情页获取个股的地址信息，并进行解析
    :param stock:
    :return:
    """
    return ak.get_stock_register_address(stock)


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