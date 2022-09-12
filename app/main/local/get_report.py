"""
财报测试
"""

import akshare as ak

stock_balance_sheet_by_report_em_df = ak.stock_balance_sheet_by_report_em(symbol="SH600519")
print(stock_balance_sheet_by_report_em_df)

stock_profit_sheet_by_report_em_df = ak.stock_profit_sheet_by_report_em(symbol="SH600519")
print(stock_profit_sheet_by_report_em_df)


stock_cash_flow_sheet_by_report_em_df = ak.stock_cash_flow_sheet_by_report_em(symbol="SH600519")
print(stock_cash_flow_sheet_by_report_em_df)

print(123)