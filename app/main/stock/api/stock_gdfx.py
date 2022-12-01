"""
股东分析，覆盖akshare的stock_gdfx_free_top_10_em
"""

import pandas as pd
import requests

from app.main.utils import collection_util


def stock_gdfx_free_top_10_em(
        symbol: str = "sh688686", date: str = "20210630"
) -> pd.DataFrame:
    """
    东方财富网-个股-十大流通股东
    https://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/Index?type=web&code=SH688686#sdltgd-0
    :param symbol: 带市场标识的股票代码
    :type symbol: str
    :param date: 报告期
    :type date: str
    :return: 十大股东
    :rtype: pandas.DataFrame
    """
    url = "https://emweb.securities.eastmoney.com/PC_HSF10/ShareholderResearch/PageSDLTGD"
    params = {
        "code": f"{symbol.upper()}",
        "date": f"{'-'.join([date[:4], date[4:6], date[6:]])}",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    if collection_util.is_empty(data_json["sdltgd"]):
        return None
    temp_df = pd.DataFrame(data_json["sdltgd"])
    temp_df.reset_index(inplace=True)
    temp_df["index"] = temp_df.index + 1
    temp_df.columns = [
        "名次",
        "-",
        "-",
        "-",
        "-",
        "股东名称",
        "股东性质",
        "股份类型",
        "持股数",
        "占总流通股本持股比例",
        "增减",
        "变动比率",
    ]
    temp_df = temp_df[
        [
            "名次",
            "股东名称",
            "股东性质",
            "股份类型",
            "持股数",
            "占总流通股本持股比例",
            "增减",
            "变动比率",
        ]
    ]
    temp_df["持股数"] = pd.to_numeric(temp_df["持股数"])
    temp_df["占总流通股本持股比例"] = pd.to_numeric(temp_df["占总流通股本持股比例"])
    temp_df["变动比率"] = pd.to_numeric(temp_df["变动比率"])

    temp_df.columns = ['index', 'gd_name', 'gd_type', 'gf_type', 'holding_num', 'holding_rate', 'is_change',
                       'change_rate']

    return temp_df
