from app.main.stock.dao import stock_dao, k_line_dao
from app.main.utils import restful, date_util
from . import rest
from flask import request
from app.main.utils import my_redis
from app.main.db.mongo import db
from datetime import datetime, timedelta
from flask import request
from collections import OrderedDict
from typing import List
from itertools import groupby
import collections


@rest.route("/stock/sync/filter", methods=['post'])
def stock_pick():
    params: dict = request.json
    board_group = {}

    t = params.get("type", "num")
    exclude_board = params.get("excludeBoard", [])

    results = get_stock_result(params)
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
        results = stock_dao.get_stock_detail_list(list(code_set), dict(name=1, _id=0))
        return restful.response(results)

    return restful.response(board_group)


@rest.route("/stock/data/miner", methods=['post'])
def data_miner():
    params: dict = request.json
    results = get_stock_result(params)
    codes = [r['stock_code'] for r in results]

    start = date_util.parse_date_time(params.get("date"), "%Y-%m-%d")
    end = date_util.parse_date_time(params.get("until"), "%Y-%m-%d")
    aim_board = params.get("aimBoard", None)
    only_cyb = params.get("onlyCyb", False)

    datas = k_line_dao.get_k_line_by_code(codes, start, end)
    group = {}
    for data in datas:
        code = data['code']
        array = group.get(code, [])
        array.append(data)
        group[code] = array

    final = {}

    boards = []
    for result in results:
        code:str = result['stock_code']
        name = result['name']
        board = result['board_list']
        boards.extend(board)

        if code not in group.keys(): continue
        if aim_board is not None and aim_board not in board: continue

        if only_cyb and code.startswith("300") is False: continue

        trade_data_list = group[code]

        close_list = [trade_data['close'] for trade_data in trade_data_list]
        a = close_list[0]
        b = max(close_list)
        index = close_list.index(b)
        high_date = trade_data_list[index]['date']
        rate = round((b - a) / a * 100, 2)

        final[name] = dict(
            rate=rate,
            high_date=high_date,
            board=board
        )

    counter = collections.Counter(boards)

    return restful.response(dict(detail=final, counter=counter.most_common(30)))


def get_stock_result(params) -> List[dict]:
    stock_feature = db['stock_feature']

    date = date_util.parse_date_time(params.get("date"), fmt="%Y-%m-%d")
    date = date if date is not None else date_util.get_start_of_day(datetime.now())
    gap = params.get("gap", None)
    up_shadow_rate = params.get("up_shadow_rate", None)
    rate = params.get("rate", None)  # ["$eq",0]
    close_rate_5 = params.get("close_rate_5", None)  # ["$eq",0]
    entity_length = params.get("entity_length", None)  # ["$gt",0]
    close = params.get("close", None)  # ["$gt",0]

    match = {"date": date, "$expr": {"$and": []}}

    volumeUp = params.get("volumeUp", None)
    if volumeUp is not None:
        match["$expr"]["$and"].append({"$gt": ["$features.volume", {"$multiply": ["$features.vol_avg_10", volumeUp]}
                                               ]})
    if gap is not None:
        match["features.gap"] = {"$in": gap}

    if up_shadow_rate is not None:
        pass

    if rate is not None:
        match["$expr"]["$and"].append({rate[0]: ["$features.rate", rate[1]]})

    if close_rate_5 is not None:
        match["$expr"]["$and"].append({close_rate_5[0]: ["$features.close_rate_5", close_rate_5[1]]})

    if entity_length is not None:
        match["$expr"]["$and"].append({entity_length[0]: ["$features.entity_length", entity_length[1]]})

    if close is not None:
        match["$expr"]["$and"].append({close[0]: ["$features.close", close[1]]})

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
    results = list(condition)
    return results
