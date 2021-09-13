import pandas as pd
import requests
import akshare as ak


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
        "beg": "0",
        "end": "20500000",
        "_": "1623766962675",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
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
    temp_df = temp_df[start_date:end_date]
    temp_df.reset_index(inplace=True, drop=True)
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
            "换手率": float,
        }
    )
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
        "fs": "m:1 t:2,m:1 t:23",
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
        "fs": "m:0 t:6,m:0 t:80",
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

def stock_board_concept_hist_em(symbol: str = "数字货币", adjust: str = "qfq",beg="0",end="20500101") -> pd.DataFrame:
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
    return temp_df

def stock_board_concept_hist_em(symbol: str = "数字货币", adjust: str = "qfq",beg="0",end="20500101") -> pd.DataFrame:
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
    fs = "m:90 f:!50"
    if t is not None:
        fs = fs+" t:{}".format(t)
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
    temp_df["最新价"] = pd.to_numeric(temp_df["最新价"])
    temp_df["涨跌额"] = pd.to_numeric(temp_df["涨跌额"])
    temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"])
    temp_df["总市值"] = pd.to_numeric(temp_df["总市值"])
    temp_df["换手率"] = pd.to_numeric(temp_df["换手率"])
    temp_df["上涨家数"] = pd.to_numeric(temp_df["上涨家数"])
    temp_df["下跌家数"] = pd.to_numeric(temp_df["下跌家数"])
    temp_df["领涨股票-涨跌幅"] = pd.to_numeric(temp_df["领涨股票-涨跌幅"])
    return temp_df

def stock_board_concept_cons_em(symbol: str = "车联网",symbol_code=None) -> pd.DataFrame:
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
