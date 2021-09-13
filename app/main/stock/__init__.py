import logging as log
from app.main.stock.api.overwrite import stock_zh_a_hist,\
    stock_ind,\
    code_id_map,\
    stock_board_concept_hist_em,\
    stock_board_concept_name_em,\
stock_board_concept_cons_em


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