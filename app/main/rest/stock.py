from app.main.stock.dao import stock_dao, k_line_dao
from app.main.stock.service import stock_service, config_service,search_udf_service,stock_search_service
from app.main.utils import restful, date_util, simple_util
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
    # 处理一下入参
    result = stock_search_service.comprehensive_search(request_body)
    return restful.response(result)


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
