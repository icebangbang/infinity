from app.main.db.mongo import db
from app.main.utils import date_util
from datetime import datetime
import pandas as pd

board_detail = db['board_detail']
trend_point_set = db['trend_point']
board = board_detail.find_one({"board": {"$in": ['电池']}})
total = board['codes']

results = list(trend_point_set.find(
                {"date": {"$lte": date_util.get_start_of_day(datetime.now())},
                 "update": {"$gte": date_util.get_start_of_day(datetime.now())},
                 "code": {"$in": total}, "trend_type": {"$in": [1, 3]}})
.sort("code", 1))

df = pd.DataFrame(results)
df = df.sort_values("update_time",ascending=False).drop_duplicates(subset=['code'],keep='first')

for result in results:
    print(result['code'])
