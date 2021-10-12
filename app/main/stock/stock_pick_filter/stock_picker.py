from app.main.stock.constant import *
from app.main.stock.dao import stock_dao
from datetime import datetime


condition = {
    ma20_incr: True,
    close_gte_ma10: True,
    kdj_golden_hit_day: {"$lt": 1}
}

stocks = stock_dao.pick_by_feature(condition,datetime.now())
print(stocks)
