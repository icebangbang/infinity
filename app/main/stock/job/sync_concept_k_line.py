import akshare as ak


from app.main.stock.dao import stock_dao
from app.main.stock.service import sync_kline_service
import logging

concepts = stock_dao.get_all_concept()
# 获取最近一个交易日

for index,concept in enumerate(concepts):
    logging.info("同步{}:{}的日k数据,时序{}".format(concept['concept'],concept["code"],index))
    r = sync_kline_service.sync_concept_k_line(concept['concept'], )
    if r is not None:
        # time.sleep(0.1)
        pass
    else:
        logging.info("已经处理过")

