"""
数据挖掘
"""
from datetime import datetime
from app.main.db.mongo import db

condition = {"$expr": {"$and": [
    {'$eq': ["$date", datetime(2022, 2, 21)]},
    {"$gte": ["$features.earning_rate_2", 10]},

]}}

r = list(db['stock_feature'].aggregate([
    {"$match": condition}
]))

for data in r:
    print(data['name'],data['code'])
