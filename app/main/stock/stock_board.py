import akshare as ak
import logging as log
import time

"""
同花顺概念相关
"""

# 获取所有概念
def get_board(type=None):
    concept_df = ak.stock_board_concept_name_em(type)
    concept_list = concept_df.to_dict(orient='records')
    return concept_list


# 获取概念关联的公司
def get_board_mapping(symbol=None,symbol_code=None):
    concept_cons_df = ak.stock_board_concept_cons_em(symbol=symbol,symbol_code=symbol_code)
    concept_cons_list = concept_cons_df.to_dict(orient='records')
    return concept_cons_list
