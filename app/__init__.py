import os, time

if hasattr(time, 'tzset'):
    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

import logging as log
from app.main.stock.api.overwrite import stock_zh_a_hist, \
    stock_ind, \
    code_id_map, \
    stock_board_concept_hist_em, \
    stock_board_concept_name_em, \
    stock_board_concept_cons_em, \
    chinese_ppi, chinese_cpi, pig_data, chinese_pmi, \
    get_stock_web, get_stock_business, get_bellwether, fund_etf_hist_sina
from app.main.stock.api.three_table_overwrite import stock_cash_flow_sheet_by_report_em,\
    stock_balance_sheet_by_report_em,stock_profit_sheet_by_report_em

log.basicConfig(
    level=log.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)

import akshare

akshare.stock_zh_a_hist = stock_zh_a_hist
akshare.stock_ind = stock_ind
akshare.code_id_map = code_id_map
akshare.stock_board_concept_hist_em = stock_board_concept_hist_em
akshare.stock_board_concept_name_em = stock_board_concept_name_em
akshare.stock_board_concept_cons_em = stock_board_concept_cons_em
akshare.chinese_ppi = chinese_ppi
akshare.chinese_cpi = chinese_cpi
akshare.chinese_pmi = chinese_pmi
akshare.pig_data = pig_data
akshare.pig_data = pig_data
akshare.get_stock_web = get_stock_web
akshare.get_stock_business = get_stock_business
akshare.get_bellwether = get_bellwether
akshare.fund_etf_hist_sina = fund_etf_hist_sina
akshare.stock_cash_flow_sheet_by_report_em = stock_cash_flow_sheet_by_report_em
akshare.stock_balance_sheet_by_report_em = stock_balance_sheet_by_report_em
akshare.stock_profit_sheet_by_report_em = stock_profit_sheet_by_report_em
