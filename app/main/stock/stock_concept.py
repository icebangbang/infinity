import akshare as ak
import logging as log
import time

"""
同花顺概念相关
"""

# 获取所有概念
def get_all_concept():
    concept_df = ak.stock_board_concept_name_em()
    concept_list = concept_df.to_dict(orient='records')
    return concept_list


# 获取概念关联的公司
def get_concept_mapping(symbol):
    concept_cons_df = ak.stock_board_concept_cons_em(symbol=symbol)
    concept_cons_list = concept_cons_df.to_dict(orient='records')
    return concept_cons_list
