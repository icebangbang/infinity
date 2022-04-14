from app.main.stock.dao import stock_dao, k_line_dao
from app.main.stock.service import stock_service, config_service
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


@rest.route("/stock/data/miner/store", methods=['post'])
def data_miner_with_store():
    request_body = request.json
    key = request_body['key']
    # 提前设置好的请求参数
    params = config_service.get_query_param(key)
    request_body.update(params)
    resp = data_miner(request_body)

    return resp


@rest.route("/stock/data/miner", methods=['post'])
def data_miner(request_body=None):
    if request_body is None:
        request_body: dict = request.json
    # 数据库检索
    results: list = stock_service.stock_search(request_body)
    codes = [r['stock_code'] for r in results]

    aim_board = request_body['custom'].get("aimBoard", None)
    only_cyb = request_body['custom'].get("onlyCyb", False)
    hide_board = request_body['custom'].get("hideBoard", False)
    only_code = request_body['custom'].get("onlyCode", False)

    start = date_util.parse_date_time(request_body.get("date"), "%Y-%m-%d")
    end = date_util.parse_date_time(request_body.get("until"), "%Y-%m-%d")

    # if date_util.get_days_between(end, start) == 0:
    start, uesless = date_util.get_work_day(start, 1)
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
                # 地域板块不加入boards,不会出现在所属板块中
                continue

            elif board not in ['融资融券', '富时罗素', '标准普尔', '预盈预增', '昨日涨停_含一字', '昨日涨停', '预亏预减'
                                                                                   '深股通', 'MSCI中国', '沪股通', '深成500',
                               '预亏预减', '深股通'
                                       '创业板综', '中证500', '上证380', '转债标的', '内贸流通', '电商概念', '机构重仓', 'QFII重仓', '长江三角']:

                boards.append(board)
        if code not in group.keys(): continue
        if aim_board is not None and aim_board not in board_list: continue

        if only_cyb and code.startswith("300") is False: continue

        trade_data_list = group[code]

        close_list = [trade_data['close'] for trade_data in trade_data_list]

        a = close_list[0]
        b = max(close_list[1:]) if len(close_list) > 1 else a
        index = close_list.index(b)
        high_date = trade_data_list[index]['date']
        rate = round((b - a) / a * 100, 2)

        final[name] = dict(
            name=name,
            rate=rate,
            code=code,
            high_date=high_date.strftime("%Y-%m-%d"),
            boards=board_list
        )
        if hide_board is True:
            final[name].__delitem__("board")

    counter = collections.Counter(boards)
    area_counter = collections.Counter(area_boards)
    final = OrderedDict(sorted(final.items(), key=lambda item: item[1]['rate'], reverse=True))

    if only_code:
        return restful.response(list(final.keys()))
    else:
        final = [item for item in final.values()]

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
    entity_length = params.get("entity_length", None)  # ["$gt",0] k线实体
    close = params['custom'].get("close", None)  # ["$gt",0]
    sma_down = params.get("sma_down", None)  # 均线空头
    sma_up = params.get("sma_up", None)  # 均线空头
    volume_up_10 = params.get("volume_up_10", None)
    volume_gt_5 = params.get("volume_gt_5", None)
    volume_lt_5 = params.get("volume_lt_5", None)
    volume_down_5 = params.get("volume_down_5", None)
    ma5_upon_20 = params.get("ma5_upon_20", None)
    ma10_upon_20 = params.get("ma10_upon_20", None)
    ma5_upon_10 = params.get("ma5_upon_10", None)
    ma10_upon_10 = params.get("ma10_upon_10", None)
    ma5_upon_5 = params.get("ma5_upon_5", None)
    ma10_upon_5 = params.get("ma10_upon_5", None)
    ma5_upon_max = params.get("ma5_upon_max", None)

    match = {"date": date, "$expr": {"$and": []}}

    '''
    if volume_up_10 is not None:
        match["$expr"]["$and"].append(
            {"$gte": ["$features.volume", {"$multiply": ["$features.vol_avg_10", volume_up_10]}
                      ]})
    if volume_gt_5 is not None:
        match["$expr"]["$and"].append({"$gte": ["$features.volume", {"$multiply": ["$features.vol_avg_5", volume_gt_5]}
                                                ]})
    if volume_lt_5 is not None:
        match["$expr"]["$and"].append({"$lte": ["$features.volume", {"$multiply": ["$features.vol_avg_5", volume_lt_5]}
                                                ]})

    if volume_down_5 is not None:
        match["$expr"]["$and"].append(
            {"$lte": ["$features.volume", {"$multiply": ["$features.vol_avg_5", volume_down_5]}
                      ]})
                      
    if sma_down:
        match["$expr"]["$and"].append({"$gt": ["$features.ma60", "$features.ma30"]})
        match["$expr"]["$and"].append({"$gt": ["$features.ma30", "$features.ma20"]})
        match["$expr"]["$and"].append({"$gt": ["$features.ma20", "$features.ma10"]})
    if sma_up:
        match["$expr"]["$and"].append({"$lt": ["$features.ma60", "$features.ma30"]})
        match["$expr"]["$and"].append({"$lt": ["$features.ma30", "$features.ma20"]})
        match["$expr"]["$and"].append({"$lt": ["$features.ma20", "$features.ma10"]})
    '''

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
