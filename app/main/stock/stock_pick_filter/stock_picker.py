from app.main.stock.dao import stock_dao
from datetime import datetime


condition = {
    "kdj_golden_hit_day": {"$lt": 1}
}

stocks = stock_dao.pick_by_feature(condition,datetime.now())
print(stocks)
