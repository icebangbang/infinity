import logging as log
from app.main.stock.overwrite import stock_zh_a_hist

log.basicConfig(
    level=log.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)

import akshare
akshare.stock_zh_a_hist = stock_zh_a_hist