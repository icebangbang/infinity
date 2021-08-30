import akshare as ak
import json
import pymongo
import pandas as pd
import logging as log


# concept = ak.stock_board_concept_name_ths()
# stock_sse_summary_df = ak.stock_sse_summary()
# print(stock_sse_summary_df)

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
