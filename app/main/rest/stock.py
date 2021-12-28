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

    aim_board = params['custom'].get("aimBoard", None)
    only_cyb = params['custom'].get("onlyCyb", False)
    hide_board = params['custom'].get("hideBoard", False)
    only_code = params['custom'].get("onlyCode", False)

    start = date_util.parse_date_time(params.get("date"), "%Y-%m-%d")
    end = date_util.parse_date_time(params.get("until"), "%Y-%m-%d")

    # if date_util.get_days_between(end, start) == 0:
    start,uesless = date_util.get_work_day(start,2)
    # start = start - timedelta(days=1)

    datas = k_line_dao.get_k_line_by_code(codes, start, end)
    group = {}
    for data in datas:
        code = data['code']
        array = group.get(code, [])
        array.append(data)
        group[code] = array

    final = {}

    boards = []
    area_boards = []
    for result in results:
        code: str = result['stock_code']
        name = result['name']
        board_list = result['board_list']

        for board in board_list:
            if "板块" in board:
                area_boards.append(board)

            elif board not in ['融资融券','富时罗素','标准普尔',
                         '深股通','MSCI中国','沪股通','深成500',
                         '创业板综','中证500','上证380','转债标的','内贸流通','电商概念','机构重仓']:

                boards.append(board)
        if code not in group.keys(): continue
        if aim_board is not None and aim_board not in board_list: continue

        if only_cyb and code.startswith("300") is False: continue

        trade_data_list = group[code]

        close_list = [trade_data['close'] for trade_data in trade_data_list]

        a = close_list[0]
        b = max(close_list[1:]) if len(close_list)>1 else a
        index = close_list.index(b)
        high_date = trade_data_list[index]['date']
        rate = round((b - a) / a * 100, 2)

        final[name] = dict(
            rate=rate,
            high_date=high_date,
            board=board_list
        )
        if hide_board is True:
            final[name].__delitem__("board")

    counter = collections.Counter(boards)
    area_counter = collections.Counter(area_boards)
    final = OrderedDict(sorted(final.items(), key=lambda item: item[1]['rate'], reverse=True))

    if only_code:
        return restful.response(list(final.keys()))

    return restful.response(dict(counter=dict(counter.most_common(20)),
                                 area_counter=dict(area_counter.most_common(10)),
                                 detail=final, size=len(final)))




def get_stock_result(params) -> List[dict]:
    stock_feature = db['stock_feature']

    date = date_util.parse_date_time(params.get("date"), fmt="%Y-%m-%d")
    date = date if date is not None else date_util.get_start_of_day(datetime.now())
    gap = params.get("gap", None)
    up_shadow_rate = params.get("up_shadow_rate", None)
    rate = params.get("rate", None)  # ["$eq",0]
    close_rate_5 = params.get("close_rate_5", None)  # ["$eq",0]
    entity_length = params.get("entityLength", None)  # ["$gt",0] k线实体
    close = params['custom'].get("close", None)  # ["$gt",0]
    sma_down = params.get("smaDown", None) # 均线空头
    sma_up = params.get("smaUp", None) # 均线空头

    match = {"date": date, "$expr": {"$and": []}}

    volumeUp10 = params.get("volumeUp10", None)
    volumeUp5 = params.get("volumeUp5", None)
    if volumeUp10 is not None:
        match["$expr"]["$and"].append({"$gt": ["$features.volume", {"$multiply": ["$features.vol_avg_10", volumeUp10]}
                                               ]})
    if volumeUp5 is not None:
        match["$expr"]["$and"].append({"$gt": ["$features.volume", {"$multiply": ["$features.vol_avg_5", volumeUp5]}
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

    if sma_down :
        match["$expr"]["$and"].append({"$gt":["$features.ma60","$features.ma30"]})
        match["$expr"]["$and"].append({"$gt":["$features.ma30","$features.ma20"]})
        match["$expr"]["$and"].append({"$gt":["$features.ma20","$features.ma10"]})
    if sma_up :
        match["$expr"]["$and"].append({"$lt":["$features.ma60","$features.ma30"]})
        match["$expr"]["$and"].append({"$lt":["$features.ma30","$features.ma20"]})
        match["$expr"]["$and"].append({"$lt":["$features.ma20","$features.ma10"]})


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
