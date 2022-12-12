from app.main.stock.service import fund_service
from app.main.utils import cal_util
import pandas as pd

def analysis_price_range(indicator:dict):
    price = indicator['close']
    df = pd.DataFrame([dict(price=price)])
    df['range'] = pd.cut(df.price, bins=[0, 5, 10, 20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000],
                         labels=["0-5", "5-10", "10-20", "20-30", "30-40", "40-50", "50-100", "100-200", "200-300",
                                 "300-400", "400-500", "500-1000", "1000-2000"],
                         include_lowest=False)
    indicator['price_range'] = df['range'][0]

def analysis_stock_price(k_line_list,indicator:dict):
    indicator['price'] = k_line_list[0]['close']



def analysis_stock_value(indicator:dict):
    """
    市值分析
    :return:
    """
    start_date = indicator['start_date']
    code = indicator['code']
    stock_value = fund_service.get_stock_value(code, start_date)
    indicator['flow_value'] = stock_value['flowCapitalValue']
    indicator['market_value'] = stock_value['MarketValue']
    # 流通股占总股本比例
    indicator['flow_rate'] = cal_util.get_rate(stock_value['flowCapitalValue'],stock_value['MarketValue'])
