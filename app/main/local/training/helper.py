from app.main.stock.service import fund_service
from app.main.utils import cal_util

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
