from app.main.db.mongo import db
from app.main.utils import date_util

board_detail = db['board_detail']
board = board_detail.find_one({"board": '半导体'})
codes = board['codes']

trend_point = db['trend_point']
r = list(trend_point.find({"code":{"$in":codes},
                           "date":date_util.get_latest_work_day(),
                           "trend":"up"}))
print(123)