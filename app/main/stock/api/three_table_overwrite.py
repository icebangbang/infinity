"""
三表报告
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from datetime import date, datetime

from app.main.utils import date_util

requests.adapters.DEFAULT_RETRIES = 5


def _stock_balance_sheet_by_report_ctype_em(symbol: str = "SH600519") -> str:
    """
    东方财富-股票-财务分析-资产负债表-按报告期-公司类型判断
    https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh601878#zcfzb-0
    :param symbol: 股票代码; 带市场标识
    :type symbol: str
    :return: 东方财富-股票-财务分析-资产负债表-按报告期-公司类型判断
    :rtype: str
    """
    url = f"https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index"
    params = {"type": "web", "code": symbol.lower()}
    r = requests.get(url, params=params)
    soup = BeautifulSoup(r.text, "lxml")
    company_type = soup.find(attrs={"id": "hidctype"})["value"]
    return company_type


def stock_profit_sheet_by_report_em(from_datetime: datetime, symbol: str = "SH600519") -> pd.DataFrame:
    """
    东方财富-股票-财务分析-利润表-报告期
    https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0
    :param symbol: 股票代码; 带市场标识
    :type symbol: str
    :return: 利润表-报告期
    :rtype: pandas.DataFrame
    """
    company_type = _stock_balance_sheet_by_report_ctype_em(symbol)
    url = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/lrbDateAjaxNew"
    params = {
        "companyType": company_type,
        "reportDateType": "0",
        "code": symbol,
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json["data"])
    temp_df["REPORT_DATE"] = pd.to_datetime(temp_df["REPORT_DATE"]).dt.date
    temp_df = temp_df[temp_df["REPORT_DATE"] >= from_datetime.date()]

    # temp_df["REPORT_DATE"] = temp_df["REPORT_DATE"].astype(str)
    need_date = temp_df["REPORT_DATE"].tolist()
    sep_list = [
        ",".join(date_util.dt_to_str(d,'%Y-%m-%d') for d in need_date[i: i + 5]) for i in range(0, len(need_date), 5)
    ]
    big_df = pd.DataFrame()
    for item in tqdm(sep_list, leave=False):
        url = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/lrbAjaxNew"
        params = {
            "companyType": company_type,
            "reportDateType": "0",
            "reportType": "1",
            "code": symbol,
            "dates": item,
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["data"])
        big_df = pd.concat([big_df, temp_df], ignore_index=True)
    return big_df


def stock_cash_flow_sheet_by_report_em(from_datetime,
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
    company_type = _stock_balance_sheet_by_report_ctype_em(symbol)
    url = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/xjllbDateAjaxNew"
    params = {
        "companyType": company_type,
        "reportDateType": "0",
        "code": symbol,
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json["data"])
    temp_df["REPORT_DATE"] = pd.to_datetime(temp_df["REPORT_DATE"]).dt.date
    temp_df = temp_df[temp_df["REPORT_DATE"] >= from_datetime.date()]
    # temp_df["REPORT_DATE"] = temp_df["REPORT_DATE"].astype(str)
    need_date = temp_df["REPORT_DATE"].tolist()
    sep_list = [
        ",".join(date_util.dt_to_str(d, '%Y-%m-%d') for d in need_date[i: i + 5]) for i in range(0, len(need_date), 5)
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


def stock_balance_sheet_by_report_em(from_datetime, symbol: str = "SH600519") -> pd.DataFrame:
    """
    东方财富-股票-财务分析-资产负债表-按报告期
    https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0
    :param symbol: 股票代码; 带市场标识
    :type symbol: str
    :return: 资产负债表-按报告期
    :rtype: pandas.DataFrame
    """
    company_type = _stock_balance_sheet_by_report_ctype_em(symbol=symbol)
    url = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/zcfzbDateAjaxNew"
    params = {
        "companyType": company_type,
        "reportDateType": "0",
        "code": symbol,
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json["data"])
    temp_df["REPORT_DATE"] = pd.to_datetime(temp_df["REPORT_DATE"]).dt.date
    temp_df = temp_df[temp_df["REPORT_DATE"] >= from_datetime.date()]
    # temp_df["REPORT_DATE"] = temp_df["REPORT_DATE"].astype(str)
    need_date = temp_df["REPORT_DATE"].tolist()
    sep_list = [
        ",".join(date_util.dt_to_str(d, '%Y-%m-%d') for d in need_date[i: i + 5]) for i in range(0, len(need_date), 5)
    ]
    big_df = pd.DataFrame()
    for item in tqdm(sep_list, leave=False):
        url = "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/zcfzbAjaxNew"
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

def stock_financial_analysis_indicator(from_year=2010,symbol: str = "600004",name="") -> pd.DataFrame:
    """
    新浪财经-财务分析-财务指标
    https://money.finance.sina.com.cn/corp/go.php/vFD_FinancialGuideLine/stockid/600004/ctrl/2019/displaytype/4.phtml
    :param symbol: 股票代码
    :type symbol: str
    :return: 新浪财经-财务分析-财务指标
    :rtype: pandas.DataFrame
    """
    url = f"https://money.finance.sina.com.cn/corp/go.php/vFD_FinancialGuideLine/stockid/{symbol}/ctrl/2020/displaytype/4.phtml"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    year_context = soup.find(attrs={"id": "con02-1"}).find("table").find_all("a")
    year_list = [item.text for item in year_context if int(item.text) >=from_year]
    out_df = pd.DataFrame()
    for year_item in tqdm(year_list, leave=False):
        url = f"https://money.finance.sina.com.cn/corp/go.php/vFD_FinancialGuideLine/stockid/{symbol}/ctrl/{year_item}/displaytype/4.phtml"
        r = requests.get(url)
        temp_df = pd.read_html(r.text)[12].iloc[:, :-1]
        temp_df.columns = temp_df.iloc[0, :]
        temp_df = temp_df.iloc[1:, :]
        big_df = pd.DataFrame()
        indicator_list = ["每股指标", "盈利能力", "成长能力", "营运能力", "偿债及资本结构", "现金流量", "其他指标"]
        for i in range(len(indicator_list)):
            if i == 6:
                inner_df = temp_df[
                    temp_df.loc[
                        temp_df.iloc[:, 0].str.find(indicator_list[i]) == 0, :
                    ].index[0] :
                ].T
            else:
                inner_df = temp_df[
                    temp_df.loc[temp_df.iloc[:, 0].str.find(indicator_list[i]) == 0, :]
                    .index[0] : temp_df.loc[
                        temp_df.iloc[:, 0].str.find(indicator_list[i + 1]) == 0, :
                    ]
                    .index[0]
                    - 1
                ].T
            inner_df = inner_df.reset_index(drop=True)
            big_df = pd.concat([big_df, inner_df], axis=1)
        big_df.columns = big_df.iloc[0, :].tolist()
        big_df = big_df.iloc[1:, :]
        big_df.index = temp_df.columns.tolist()[1:]
        out_df = pd.concat([out_df, big_df])

    out_df.dropna(inplace=True)
    out_df.reset_index(inplace=True)
    out_df.rename(columns={'index': 'date',
                           "加权净资产收益率(%)":"weighted_roe",
                           "净资产收益率(%)":"roe"}, inplace=True)
    out_df['date'] = pd.to_datetime(out_df['date'], format='%Y-%m-%d')
    out_df['code'] = symbol
    out_df['name'] = name
    return out_df


if __name__ == "__main__":
    import akshare
    r = stock_financial_analysis_indicator(symbol="600030")
    print(123)
    # stock_balance_zyzb_report_em(datetime(2010, 1, 1),"SH600030")
