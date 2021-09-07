import logging as log
from app.main.stock.overwrite import stock_zh_a_hist
from app.main.stock.overwrite import stock_ind
from app.main.stock.overwrite import code_id_map

log.basicConfig(
    level=log.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)

import akshare
akshare.stock_zh_a_hist = stock_zh_a_hist
akshare.stock_ind = stock_ind
akshare.code_id_map = code_id_map