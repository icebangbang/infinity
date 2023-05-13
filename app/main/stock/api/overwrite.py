import json
from app.log import get_logger
from datetime import datetime
from functools import lru_cache

import akshare as ak
import dateutil
import jionlp as jio
import pandas as pd
import requests
from akshare.stock.cons import hk_js_decode
from akshare.utils import demjson
from bs4 import BeautifulSoup
from py_mini_racer import py_mini_racer
from requests.exceptions import ProxyError
from tqdm import tqdm
import time

from app.main.stock.dao import stock_dao
from app.main.utils import simple_util

log = get_logger(__name__)

def stock_zh_a_hist(
        symbol: str = "600070",
        start_date: str = "19700101",
        end_date: str = "22220101",
        adjust: str = "",
        klt: str = "101",
        code_id_dict=None
) -> pd.DataFrame:
    """
    东方财富网-行情首页-上证 A 股-每日行情
    http://quote.eastmoney.com/concept/sh603777.html?from=classic
    :param symbol: 股票代码
    :type symbol: str
    :param start_date: 开始日期
    :type start_date: str
    :param end_date: 结束日期
    :type end_date: str
    :param adjust: choice of {"qfq": "1", "hfq": "2", "": "不复权"}
    :type adjust: str
    :param klt: choice of {"月k": "103", "日k": "101", "周k": "102","1分钟":1}
    :type adjust: str
    :return: 每日行情
    :rtype: pandas.DataFrame
    """
    if code_id_dict is None:
        code_id_dict = _code_id_map()
    adjust_dict = {"qfq": "1", "hfq": "2", "": "0"}
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": klt,
        "fqt": adjust_dict[adjust],
        "secid": f"{code_id_dict[symbol]}.{symbol}",
        "beg": start_date,
        "end": end_date,
        "_": "1623766962675",
    }
    while True:
        try:
            r = requests.get(url, params=params)
            log.info(r.text)
            break
        except Exception as e:
            log.error(e, exc_info=1)
    data_json = r.json()
    data = data_json["data"]
    if data is None: return None
    prev_k_price = data['preKPrice']
    temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["klines"]])
    if temp_df.empty: return None
    temp_df.columns = [
        "日期",
        "开盘",
        "收盘",
        "最高",
        "最低",
        "成交量",
        "成交额",
        "振幅",
        "涨跌幅",
        "涨跌额",
        "换手率",
    ]

    # temp_df.index = pd.to_datetime(temp_df["日期"])
    # temp_df = temp_df[start_date:end_date]
    # temp_df.reset_index(inplace=True, drop=True)
    temp_df = temp_df.astype(
        {
            "开盘": float,
            "收盘": float,
            "最高": float,
            "最低": float,
            "成交量": int,
            "成交额": float,
            "振幅": float,
            "涨跌幅": float,
            "涨跌额": float,
            "换手率": float
        }
    )
    temp_df['最近收盘'] = temp_df.loc[temp_df['收盘'].shift(-1) > 0, '收盘']
    temp_df['最近收盘'] = temp_df['最近收盘'].shift()
    # temp_df['最近收盘'][0] = prev_k_price
    temp_df.loc[0, '最近收盘'] = prev_k_price
    return temp_df


def _code_id_map() -> dict:
    """
    东方财富-股票和市场代码
    http://quote.eastmoney.com/center/gridlist.html#hs_a_board
    :return: 股票和市场代码
    :rtype: dict
    """
    url = "http://80.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "5000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:1+t:2,m:1+t:23",
        "fields": "f12",
        "_": "1623833739532",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json["data"]["diff"])
    temp_df["market_id"] = 1
    temp_df.columns = ["sh_code", "sh_id"]
    code_id_dict = dict(zip(temp_df["sh_code"], temp_df["sh_id"]))
    params = {
        "pn": "1",
        "pz": "5000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:0+t:6,m:0+t:80",
        "fields": "f12",
        "_": "1623833739532",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    temp_df_sz = pd.DataFrame(data_json["data"]["diff"])
    temp_df_sz["sz_id"] = 0
    code_id_dict.update(dict(zip(temp_df_sz["f12"], temp_df_sz["sz_id"])))
    return code_id_dict


def stock_ind(symbol, code_id_dict=None):
    """
    MarketValue f116,市值
    PERation f162,市盈率(动),动态市盈率，总市值除以全年预估净利润，例如当前一季度净利润1000万，则预估全年净利润4000万
    staticPERation f163,静态市盈率,静态市盈率，总市值除以上一年度净利润
    RollingPERations f164,滚动市盈率 滚动市盈率，最新价除以最近4个季度的每股收益
    :param symbol:
    :return:
    """
    url = "http://push2his.eastmoney.com/api/qt/stock/get"
    if code_id_dict is None:
        code_id_dict = _code_id_map()
    params = {
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "fltt": 2,
        "invt": 2,
        "fields": "f116,f117,f162,f163,f164",
        "secid": f"{code_id_dict[symbol]}.{symbol}"
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    df = pd.DataFrame([data_json["data"]])
    df.columns = [
        "MarketValue",
        "flowCapitalValue",
        "PERation",
        "staticPERation",
        "RollingPERations"
    ]
    df.loc[df["MarketValue"] == '-', ["MarketValue"]] = 0
    df.loc[df["flowCapitalValue"] == '-', ["flowCapitalValue"]] = 0
    df.loc[df["staticPERation"] == '-', ["staticPERation"]] = 0
    df.loc[df["PERation"] == '-', ["PERation"]] = 0
    df.loc[df["RollingPERations"] == '-', ["RollingPERations"]] = 0
    df = df.astype(
        {
            "MarketValue": float,
            "flowCapitalValue": float,
            "PERation": float,
            "staticPERation": float,
            "RollingPERations": float,
        }
    )
    df['code'] = symbol
    return df


def code_id_map():
    return _code_id_map()


def stock_board_concept_hist_em(symbol: str = "数字货币", adjust: str = "qfq", beg="0", end="20500101") -> pd.DataFrame:
    """
    东方财富-沪深板块-概念板块-历史行情
    http://quote.eastmoney.com/bk/90.BK0715.html
    :param symbol: 板块名称
    :type symbol: str
    :param adjust: choice of {'': 不复权, "qfq": 前复权, "hfq": 后复权}
    :type adjust: str
    :return: 历史行情
    :rtype: pandas.DataFrame
    """
    stock_board_concept_em_map = ak.stock_board_concept_name_em()
    stock_board_code = stock_board_concept_em_map[
        stock_board_concept_em_map["板块名称"] == symbol
        ]["板块代码"].values[0]
    adjust_map = {"": "0", "qfq": "1", "hfq": "2"}
    url = "http://91.push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": f"90.{stock_board_code}",
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": "101",
        "fqt": adjust_map[adjust],
        "beg": beg,
        "end": end,
        "smplmt": "10000",
        "lmt": "1000000",
        "_": "1626079488673",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    data = data_json["data"]
    prev_k_price = data['preKPrice']
    if len(data_json["data"]["klines"]) == 0:
        return None
        # return pd.DataFrame(['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额','最近收盘'])
    temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["klines"]])
    temp_df.columns = [
        "日期",
        "开盘",
        "收盘",
        "最高",
        "最低",
        "成交量",
        "成交额",
        "振幅",
        "涨跌幅",
        "涨跌额",
        "换手率",
    ]
    temp_df = temp_df[
        [
            "日期",
            "开盘",
            "收盘",
            "最高",
            "最低",
            "涨跌幅",
            "涨跌额",
            "成交量",
            "成交额",
            "振幅",
            "换手率",
        ]
    ]
    temp_df["开盘"] = pd.to_numeric(temp_df["开盘"])
    temp_df["收盘"] = pd.to_numeric(temp_df["收盘"])
    temp_df["最高"] = pd.to_numeric(temp_df["最高"])
    temp_df["最低"] = pd.to_numeric(temp_df["最低"])
    temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"])
    temp_df["涨跌额"] = pd.to_numeric(temp_df["涨跌额"])
    temp_df["成交量"] = pd.to_numeric(temp_df["成交量"])
    temp_df["成交额"] = pd.to_numeric(temp_df["成交额"])
    temp_df["振幅"] = pd.to_numeric(temp_df["振幅"])
    temp_df["换手率"] = pd.to_numeric(temp_df["换手率"])

    temp_df['最近收盘'] = temp_df.loc[temp_df['收盘'].shift(-1) > 0, '收盘']
    temp_df['最近收盘'] = temp_df['最近收盘'].shift()
    temp_df.loc[0, '最近收盘'] = prev_k_price
    return temp_df


def stock_board_concept_name_em(t=None) -> pd.DataFrame:
    """
    东方财富-沪深板块-概念或者板块-名称
    http://quote.eastmoney.com/center/boardlist.html#concept_board
    :return: 概念板块-名称
    :rtype: pandas.DataFrame
    t=None 全部属性,地域,概念,行业
    t=1 地域
    t=2 行业
    t=3 概念
    """
    fs = "m:90+f:!50"
    if t is not None:
        fs = fs + " t:{}".format(t)
    url = "http://79.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "2000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": fs,
        "fields": "f2,f3,f4,f8,f12,f14,f15,f16,f17,f18,f20,f21,f24,f25,f22,f33,f11,f62,f128,f124,f107,f104,f105,f136",
        "_": "1626075887768",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json["data"]["diff"])
    temp_df.reset_index(inplace=True)
    temp_df["index"] = range(1, len(temp_df) + 1)
    temp_df.columns = [
        "排名",
        "最新价",
        "涨跌幅",
        "涨跌额",
        "换手率",
        "_",
        "板块代码",
        "板块名称",
        "_",
        "_",
        "_",
        "_",
        "总市值",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "上涨家数",
        "下跌家数",
        "_",
        "_",
        "领涨股票",
        "_",
        "_",
        "领涨股票-涨跌幅",
    ]
    temp_df = temp_df[
        [
            "排名",
            "板块名称",
            "板块代码",
            "最新价",
            "涨跌额",
            "涨跌幅",
            "总市值",
            "换手率",
            "上涨家数",
            "下跌家数",
            "领涨股票",
            "领涨股票-涨跌幅",
        ]
    ]
    temp_df["最新价"] = pd.to_numeric(temp_df["最新价"], errors="coerce")
    temp_df["涨跌额"] = pd.to_numeric(temp_df["涨跌额"], errors="coerce")
    temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
    temp_df["总市值"] = pd.to_numeric(temp_df["总市值"], errors="coerce")
    temp_df["换手率"] = pd.to_numeric(temp_df["换手率"], errors="coerce")
    temp_df["上涨家数"] = pd.to_numeric(temp_df["上涨家数"], errors="coerce")
    temp_df["下跌家数"] = pd.to_numeric(temp_df["下跌家数"], errors="coerce")
    temp_df["领涨股票-涨跌幅"] = pd.to_numeric(temp_df["领涨股票-涨跌幅"], errors="coerce")
    return temp_df


def stock_board_concept_cons_em(symbol: str = "车联网", symbol_code=None) -> pd.DataFrame:
    """
    东方财富-沪深板块-概念板块-板块成份
    http://quote.eastmoney.com/center/boardlist.html#boards-BK06551
    :param symbol: 板块名称
    :type symbol: str
    :return: 板块成份
    :rtype: pandas.DataFrame
    """
    if symbol_code is None:
        stock_board_concept_em_map = stock_board_concept_name_em()
        stock_board_code = stock_board_concept_em_map[
            stock_board_concept_em_map["板块名称"] == symbol
            ]["板块代码"].values[0]
    else:
        stock_board_code = symbol_code
    url = "http://29.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "2000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": f"b:{stock_board_code} f:!50",
        "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152,f45",
        "_": "1626081702127",
    }
    r = requests.get(url, params=params)
    data_json = r.json()

    temp_df = pd.DataFrame(data_json["data"]["diff"])
    temp_df.reset_index(inplace=True)
    temp_df["index"] = range(1, len(temp_df) + 1)
    temp_df.columns = [
        "序号",
        "_",
        "最新价",
        "涨跌幅",
        "涨跌额",
        "成交量",
        "成交额",
        "振幅",
        "换手率",
        "市盈率-动态",
        "_",
        "_",
        "代码",
        "_",
        "名称",
        "最高",
        "最低",
        "今开",
        "昨收",
        "_",
        "_",
        "_",
        "市净率",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
        "_",
    ]
    temp_df = temp_df[
        [
            "序号",
            "代码",
            "名称",
            "最新价",
            "涨跌幅",
            "涨跌额",
            "成交量",
            "成交额",
            "振幅",
            "最高",
            "最低",
            "今开",
            "昨收",
            "换手率",
            "市盈率-动态",
            "市净率",
        ]
    ]
    temp_df["最新价"] = pd.to_numeric(temp_df["最新价"], errors="coerce")
    temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
    temp_df["涨跌额"] = pd.to_numeric(temp_df["涨跌额"], errors="coerce")
    temp_df["成交量"] = pd.to_numeric(temp_df["成交量"], errors="coerce")
    temp_df["成交额"] = pd.to_numeric(temp_df["成交额"], errors="coerce")
    temp_df["振幅"] = pd.to_numeric(temp_df["振幅"], errors="coerce")
    temp_df["最高"] = pd.to_numeric(temp_df["最高"], errors="coerce")
    temp_df["最低"] = pd.to_numeric(temp_df["最低"], errors="coerce")
    temp_df["今开"] = pd.to_numeric(temp_df["今开"], errors="coerce")
    temp_df["昨收"] = pd.to_numeric(temp_df["昨收"], errors="coerce")
    temp_df["换手率"] = pd.to_numeric(temp_df["换手率"], errors="coerce")
    temp_df["市盈率-动态"] = pd.to_numeric(temp_df["市盈率-动态"], errors="coerce")
    temp_df["市净率"] = pd.to_numeric(temp_df["市净率"], errors="coerce")
    return temp_df


def chinese_ppi():
    """
    工业品出厂价格指数是反映全部工业产品出厂价格总水平的变动趋势和程度的相对数。
    重要性非常高：
    工业品出厂价格指数是衡量工业企业产品出厂价格变动趋势和变动程度的指数，
    是反映某一时期生产领域价格变动情况的重要经济指标，也是制定有关经济政策和国民经济核算的重要依据。
    :return:
    """
    url = "https://datainterface.eastmoney.com/EM_DataCenter/JS.aspx"
    params = {
        "type": "GJZB",
        "sty": "ZGZB",
        "ps": 200,
        "mkt": 22
    }
    r = requests.get(url, params=params)
    content = r.text
    content = content.replace("(", "").replace(")", "")
    return json.loads(content)


def chinese_cpi():
    """
    工业品出厂价格指数是反映全部工业产品出厂价格总水平的变动趋势和程度的相对数。
    重要性非常高：
    工业品出厂价格指数是衡量工业企业产品出厂价格变动趋势和变动程度的指数，
    是反映某一时期生产领域价格变动情况的重要经济指标，也是制定有关经济政策和国民经济核算的重要依据。
    :return:
    """
    url = "https://datainterface.eastmoney.com/EM_DataCenter/JS.aspx"
    params = {
        "type": "GJZB",
        "sty": "ZGZB",
        "ps": 200,
        "mkt": 19
    }
    r = requests.get(url, params=params)
    content = r.text
    content = content.replace("(", "").replace(")", "")
    return json.loads(content)


def chinese_pmi():
    """
    工业品出厂价格指数是反映全部工业产品出厂价格总水平的变动趋势和程度的相对数。
    重要性非常高：
    工业品出厂价格指数是衡量工业企业产品出厂价格变动趋势和变动程度的指数，
    是反映某一时期生产领域价格变动情况的重要经济指标，也是制定有关经济政策和国民经济核算的重要依据。
    :return:
    """
    url = "https://datainterface.eastmoney.com/EM_DataCenter/JS.aspx"
    params = {
        "type": "GJZB",
        "sty": "ZGZB",
        "ps": 200,
        "mkt": 21
    }
    r = requests.get(url, params=params)
    content = r.text
    content = content.replace("(", "").replace(")", "")
    return json.loads(content)


def pig_data():
    """
    获取农业部猪肉相关数据
    :return:
    """
    now = datetime.now()
    start_time = datetime(2021, 3, 1)
    current = start_time
    flag = True
    results = []
    while flag:
        current = current + dateutil.relativedelta.relativedelta(months=1)
        if current < datetime(2021, 12, 1):
            url = "http://www.moa.gov.cn/ztzl/szcpxx/jdsj/" + datetime.strftime(current, "%Y%m")
        else:
            url = "http://www.moa.gov.cn/ztzl/szcpxx/jdsj/{}/{}".format(current.year,
                                                                        datetime.strftime(current, "%Y%m"))
        r = requests.get(url)

        if r.status_code == 404:
            # url = "http://www.moa.gov.cn/ztzl/szcpxx/jdsj/"
            flag = False
            continue
            # r = requests.get(url)
        text = str(r.content, 'utf8')
        temp_df = pd.read_html(text)[0]

        keys = ['能繁母猪存栏', '生猪存栏', '生猪出栏', '月份规模以上生猪定点屠宰企业屠宰量', '猪肉产量']

        for index, row in temp_df.iterrows():
            indicator = row['指标']
            for key in keys:
                if key in indicator:
                    result = dict(date=current)
                    results.append(result)
                    result['name'] = key
                    num = row['数值']
                    if "（" in num:
                        num = num[0:num.index("（")]
                    if num == '—':
                        num = None

                    result['num'] = num
                    result['tb'] = row['同比']
                    hb = row['环比']

                    if hb == '—': hb = None
                    result['hb'] = hb

        if flag is False:
            break
    return results


def get_stock_web(stock):
    belong = stock['belong']
    code = stock['code']
    url = "https://emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/PageAjax?code={}{}".format(belong, code)
    r = requests.get(url)
    json_data = r.json()
    web = json_data['jbzl'][0]['ORG_WEB']
    if web is None:
        return None
    return "http://{}".format(web.split('/')[0])


def get_stock_register_address(stock):
    """
    001267
    :param stock:
    :return:
    """
    belong = stock['belong']
    code = stock['code']
    url = "https://emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/PageAjax?code={}{}".format(belong, code)
    r = requests.get(url)
    json_data = r.json()
    reg_address = json_data['jbzl'][0]['REG_ADDRESS']
    web = json_data['jbzl'][0]['ORG_WEB']
    if reg_address is None:
        return None

    address_info = jio.parse_location(reg_address)

    if address_info['province'] is None:
        stock_detail = stock_dao.get_one_stock(code)
        boards = stock_detail['board']
        province = boards[0].replace("板块", "省")
        reg_address = province + reg_address
        address_info = jio.parse_location(reg_address)

    return {"province": address_info["province"],
            "city": address_info["city"],
            "county": address_info["county"],
            "full_location": address_info["full_location"],
            "web": web}


def get_stock_business(stock):
    """
    获取个股竟经营分析情况
    :param stock:
    :return:
    """
    belong = stock['belong']
    code = stock['code']
    url = "https://emweb.securities.eastmoney.com/PC_HSF10/BusinessAnalysis/PageAjax?code={}{}".format(belong, code)
    r = requests.get(url)
    json_data = r.json()
    # 经营评述
    jyps = json_data['jyps'][0]['BUSINESS_REVIEW']
    zygcfx = json_data['zygcfx']

    return dict(jyps=jyps, zygcfx=zygcfx)


def get_bellwether():
    """
    获取龙头和领头羊
    :return:
    """
    url = "https://66.push2.eastmoney.com/api/qt/clist/get"
    params = dict(
        pn=1,
        pz=100,
        po=1,
        np=1,
        ut="bd1d9ddb04089700cf9c27f6f7426281",
        fltt=2,
        invt=2,
        wbp2u="|0|0|0|web",
        fid="f3",
        fs="m:90 t:2 f:!50",
        t=2,
        f="!50",
        # fields="f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152,f124,f107,f104,f105,f140,f141,f207,f208,f209,f222"
        fields="f14,f128,f136,f140"
    )
    resp = requests.get(url, params)
    result = resp.json()
    data_list = result['data']['diff']
    data_list = [dict(
        industry=data['f14'],
        bellwether=data['f128'],
        bellwether_rate=data['f136'],
        bellwhther_code=data['f140']
    ) for data in data_list]
    return data_list


def fund_etf_basic_info_sina(symbol: str = "159996") -> dict:
    """
    ETF 基金的基本信息，主要目的是为了获取基金规模
    http://finance.sina.com.cn/fund/quotes/000001/bc.shtml
    :param symbol:
    :return:
    """
    headers = {'Connection': 'close', }

    url = f"https://stock.finance.sina.com.cn/fundInfo/api/openapi.php/FundPageInfoService.tabjjgk?symbol={symbol}"
    while True:
        try:
            r = requests.get(url,headers=headers)
            body = r.json()['result']['data']

            return dict(
                name=body['jjjc'],  # 基金简称
                code=body['symbol'],
                start_time=body['clrq'],  # 成立时间
                body=body['jjgm'],  # 体量
                company = body['glr'], #管理公司
                style = body['FinanceStyle'], #管理公司
            )
        except ProxyError:
            time.sleep(1)

def fund_portfolio_hold_em(
    symbol: str = "162411", date: str = "2020"
) -> pd.DataFrame:
    """
    天天基金网-基金档案-投资组合-基金持仓
    http://fundf10.eastmoney.com/ccmx_000001.html
    :param symbol: 基金代码
    :type symbol: str
    :param date: 查询年份
    :type date: str
    :return: 基金持仓
    :rtype: pandas.DataFrame
    """
    url = "http://fundf10.eastmoney.com/FundArchivesDatas.aspx"
    params = {
        "type": "jjcc",
        "code": symbol,
        "topline": "200",
        "year": date,
        "month": "",
        "rt": "0.913877030254846",
    }
    r = requests.get(url, params=params)
    data_text = r.text
    data_json = demjson.decode(data_text[data_text.find("{") : -1])

    if simple_util.is_empty(data_json["content"]):
        return pd.DataFrame()

    soup = BeautifulSoup(data_json["content"], "lxml")
    item_label = [
        item.text.split("\xa0\xa0")[1]
        for item in soup.find_all("h4", attrs={"class": "t"})
    ]
    big_df = pd.DataFrame()
    for item in range(len(item_label)):
        temp_df = pd.read_html(data_json["content"], converters={"股票代码": str})[
            item
        ]
        del temp_df["相关资讯"]
        temp_df["占净值比例"] = (
            temp_df["占净值比例"].str.split("%", expand=True).iloc[:, 0]
        )
        temp_df.rename(
            columns={"持股数（万股）": "持股数", "持仓市值（万元）": "持仓市值"}, inplace=True
        )
        temp_df.rename(
            columns={"持股数（万股）": "持股数", "持仓市值（万元人民币）": "持仓市值"}, inplace=True
        )
        temp_df["季度"] = item_label[item]
        temp_df = temp_df[
            [
                "序号",
                "股票代码",
                "股票名称",
                "占净值比例",
                "持股数",
                "持仓市值",
                "季度",
            ]
        ]
        big_df = pd.concat([big_df, temp_df], ignore_index=True)
    big_df["占净值比例"] = pd.to_numeric(big_df["占净值比例"], errors="coerce")
    big_df["持股数"] = pd.to_numeric(big_df["持股数"], errors="coerce")
    big_df["持仓市值"] = pd.to_numeric(big_df["持仓市值"], errors="coerce")
    big_df["序号"] = range(1, len(big_df) + 1)
    return big_df




def fund_etf_hist_sina(symbol: str = "sz159996") -> pd.DataFrame:
    """
    ETF 基金的日行情数据
    http://finance.sina.com.cn/fund/quotes/159996/bc.shtml
    :param symbol: 基金名称, 可以通过 fund_etf_category_sina 函数获取
    :type symbol: str
    :return: ETF 基金的日行情数据
    :rtype: pandas.DataFrame
    """
    url = f"https://finance.sina.com.cn/realstock/company/{symbol}/hisdata/klc_kl.js"
    r = requests.get(url)
    js_code = py_mini_racer.MiniRacer()
    js_code.eval(hk_js_decode)
    dict_list = js_code.call('d', r.text.split("=")[1].split(";")[0].replace('"', ""))  # 执行js解密代码
    temp_df = pd.DataFrame(dict_list)
    temp_df["date"] = pd.to_datetime(temp_df["date"]).dt.date
    return temp_df


def stock_cash_flow_sheet_by_report_em(
        symbol: str = "SH600519",
) -> pd.DataFrame:
    """
    东方财富-股票-财务分析-现金流量表-按报告期
    https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0
    :param symbol: 股票代码; 带市场标识
    :type symbol: str
    :return: 现金流量表-按报告期
    :rtype: pandas.DataFrame
    """
    company_types = [4, 3, 1, 0]
    true_company_type = -1
    for company_type in company_types:
        url = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/xjllbDateAjaxNew"
        params = {
            "companyType": company_type,
            "reportDateType": "0",
            "code": symbol,
        }
        r = requests.get(url, params=params)
        data_json: dict = r.json()
        true_company_type = company_type
        if 'data' in data_json.keys(): break
    temp_df = pd.DataFrame(data_json["data"])
    temp_df["REPORT_DATE"] = pd.to_datetime(temp_df["REPORT_DATE"]).dt.date
    temp_df["REPORT_DATE"] = temp_df["REPORT_DATE"].astype(str)
    need_date = temp_df["REPORT_DATE"].tolist()
    sep_list = [
        ",".join(need_date[i: i + 5]) for i in range(0, len(need_date), 5)
    ]
    big_df = pd.DataFrame()
    for item in tqdm(sep_list, leave=False):
        url = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/xjllbAjaxNew"
        params = {
            "companyType": company_type,
            "reportDateType": "0",
            "reportType": "1",
            "dates": item,
            "code": symbol,
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["data"])
        big_df = pd.concat([big_df, temp_df], ignore_index=True)
    return big_df

@lru_cache()
def _fund_etf_code_id_map_em() -> dict:
    """
    东方财富-ETF 代码和市场标识映射
    https://quote.eastmoney.com/center/gridlist.html#fund_etf
    :return: ETF 代码和市场标识映射
    :rtype: pandas.DataFrame
    """
    url = "http://88.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "5000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "wbp2u": "|0|0|0|web",
        "fid": "f3",
        "fs": "b:MK0021,b:MK0022,b:MK0023,b:MK0024",
        "fields": "f12,f13",
        "_": "1672806290972",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json["data"]["diff"])
    temp_dict = dict(zip(temp_df["f12"], temp_df["f13"]))
    return temp_dict

def fund_etf_hist_em(
    symbol: str = "159707",
    period: str = "daily",
    start_date: str = "19700101",
    end_date: str = "20500101",
    adjust: str = "",
) -> pd.DataFrame:
    """
    东方财富-ETF 行情
    https://quote.eastmoney.com/sz159707.html
    :param symbol: ETF 代码
    :type symbol: str
    :param period: choice of {'daily', 'weekly', 'monthly'}
    :type period: str
    :param start_date: 开始日期
    :type start_date: str
    :param end_date: 结束日期
    :type end_date: str
    :param adjust: choice of {"qfq": "前复权", "hfq": "后复权", "": "不复权"}
    :type adjust: str
    :return: 每日行情
    :rtype: pandas.DataFrame
    """
    code_id_dict = _fund_etf_code_id_map_em()
    if symbol not in code_id_dict.keys():
        log.warn("暂时没有该基金的k线:{}".format(symbol))
        return None
    adjust_dict = {"qfq": "1", "hfq": "2", "": "0"}
    period_dict = {"daily": "101", "weekly": "102", "monthly": "103"}
    url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f116",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": period_dict[period],
        "fqt": adjust_dict[adjust],
        "secid": f"{code_id_dict[symbol]}.{symbol}",
        "beg": start_date,
        "end": end_date,
        "_": "1623766962675",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    if not (data_json["data"] and data_json["data"]["klines"]):
        return pd.DataFrame()
    temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["klines"]])
    temp_df.columns = [
        "日期",
        "开盘",
        "收盘",
        "最高",
        "最低",
        "成交量",
        "成交额",
        "振幅",
        "涨跌幅",
        "涨跌额",
        "换手率",
    ]
    temp_df.index = pd.to_datetime(temp_df["日期"])
    temp_df.reset_index(inplace=True, drop=True)

    temp_df["开盘"] = pd.to_numeric(temp_df["开盘"])
    temp_df["收盘"] = pd.to_numeric(temp_df["收盘"])
    temp_df["最高"] = pd.to_numeric(temp_df["最高"])
    temp_df["最低"] = pd.to_numeric(temp_df["最低"])
    temp_df["成交量"] = pd.to_numeric(temp_df["成交量"])
    temp_df["成交额"] = pd.to_numeric(temp_df["成交额"])
    temp_df["振幅"] = pd.to_numeric(temp_df["振幅"])
    temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"])
    temp_df["涨跌额"] = pd.to_numeric(temp_df["涨跌额"])
    temp_df["换手率"] = pd.to_numeric(temp_df["换手率"])
    return temp_df


if __name__ == "__main__":
    # results = stock_board_concept_name_em()
    # r = chinese_cpi()
    # r = get_stock_web(dict(code="300763",belong="sz"))
    # r = get_bellwether()
    # df = ak.fund_etf_hist_sina(symbol="sz169103")
    # df = stock_cash_flow_sheet_by_report_em(symbol="sz300763")
    df = get_stock_register_address(dict(belong='sz', code="300763"))
    print(123)
