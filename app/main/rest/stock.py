from app.main.stock.dao import stock_dao
from app.main.utils import restful, date_util
from . import rest
from flask import request
from app.main.utils import my_redis
from app.main.db.mongo import db
from datetime import datetime, timedelta
from flask import request
from collections import OrderedDict


@rest.route("/stock/sync/filter", methods=['post'])
def stock_pick():
    stock_feature = db['stock_feature']
    params: dict = request.json

    date = date_util.parse_date_time(params.get("date"), fmt="%Y-%m-%d")
    date = date if date is not None else date_util.get_start_of_day(datetime.now())
    t = params.get("type", "num")
    exclude_board = params.get("excludeBoard", [])
    gap = params.get("type", "num")

    match = {"$expr":
                 {"$gt": ["$features.volume",
                          {"$multiply": ["$features.vol_avg_10", params.get("volumeUp", 2)]
                           }
                          ]
                  },
             "date": date,
             "features.gap": {"$in":[1]}
             }

    condition = stock_feature.aggregate([
        {"$match": match},
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
        features = result['features']
        name = result['name']

        for board in board_list:
            if "板块" in board or board in exclude_board: continue
            codes = board_group.get(board, [])
            codes.append(code)
            board_group[board] = codes

    if t == "num":
        board_group = {k: len(v) for k, v in board_group.items()}
        board_group = OrderedDict(sorted(board_group.items(), key=lambda item: item[1], reverse=True))
    elif t == "codes":
        code_set = set()
        for k, v in board_group.items():
            code_set.update(v)
        results = stock_dao.get_stock_detail_list(list(code_set),dict(name=1,_id=0))
        return restful.response(results)

    return restful.response(board_group)
