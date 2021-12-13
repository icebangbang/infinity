from app.main.utils import restful, date_util
from . import rest
from flask import request
from app.main.utils import my_redis
from app.main.db.mongo import db
from datetime import datetime, timedelta
from flask import request


@rest.route("/stock/sync/filter", methods=['get'])
def stock_pick():
    stock_feature = db['stock_feature']

    r = stock_feature.find_one({"code": "300763"})

    condition = stock_feature.aggregate([
        {"$match":
             {"$expr": {"$gt": ["$features.current_vol", {"$multiply": ["$features.vol_avg_10", 2]}]},
              "date": date_util.get_start_of_day(datetime.now())
              }
         },
        {
            "$lookup": {
                "from": "stock_detail",
                "localField": "code",
                'foreignField': "code",
                "as": "result"
            },
        }, {
            "$project": {"_id": 0, "features": 1, "name": 1, "stock_code": "$result.code",
                         "board_list": "$result.board"}
        },
        {"$unwind": "$stock_code"},
        {"$unwind": "$board_list"}

    ])
    board_group = {}
    results = list(condition)
    for result in results:
        code = result['stock_code']
        board_list = result['board_list']
        for board in board_list:
            if "板块" in board: continue
            codes = board_group.get(board, [])
            codes.append(code)
            board_group[board] = codes

    return restful.response(board_group)
