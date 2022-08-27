"""
趋势点异常检测
"""


from app.main.db.mongo import db

trend_point_set = db['trend_point']

stock_detail = db['stock_detail']

stocks = list(stock_detail.find({}))

for stock in stocks:
    code = stock['code']
    # code = "300763"
    trend_point_list = list(trend_point_set.find({"code": code,
                                                  },
                                                 sort=[("date", -1), ("_id", -1)]).limit(10))
    v = sum([trend_point['is_in_use'] for trend_point in trend_point_list])
    if v > 1:
        print("{} find bug".format(code))
