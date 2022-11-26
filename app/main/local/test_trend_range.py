from datetime import datetime

from app.main.db.mongo import db

trend_data = db['trend_data']

trend_data_list = list(trend_data.find({"industry": "光伏设备",
                                        "date": {"$gte": datetime(2022, 1, 1), "$lte": datetime(2022, 12, 1)},
                                        "trend": "up"}))
rate_list = [data['rate'] for data in trend_data_list]

# 先确定当前是上行趋势还是下行趋势，定个调

store = {}

is_new_trend = True
current_index = 0
extreme = 0
start_index = 0

while current_index<len(rate_list):



    current = rate_list[current_index]
    nxt = rate_list[current_index + 1]

    if nxt>current:
        extreme = nxt

    if is_new_trend:
        start_index = current_index
        store[start_index] = dict(start_index = start_index)
        is_new_trend = False

    current_index = current_index+1