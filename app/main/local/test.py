from app.main.utils import date_util
from datetime import datetime
from app.main.db.mongo import db

stocks = list(db['k_line_day'].find({
    "date": date_util.get_latest_work_day(),
    "close": {"$gt": 5, "$lte": 15},
    "code": {'$regex': '^00'}
}))

codes = [stock['code'] for stock in stocks]

d = list(db['stock_detail'].find({"code": {"$in": codes},
                                  "MarketValue": {"$lte": 200},
                                  "board": {"$nin": ["房地产开发", "房地产服务", "河南板块", "水泥建材"
                                                     "工程咨询服务"]}},

                                 projection={"_id": 0, "name": 1, "industry": 1,
                                          }

                                 ))

print(d)
