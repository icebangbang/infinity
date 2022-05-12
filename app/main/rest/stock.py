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

@rest.route("/stock/deviation", methods=['get'])
def offset_cal():
    """
    股市偏离值计算
    """
    code = request.args.get("code")
    result =  stock_service.cal_stock_deviation(code,10)

    return restful.response(result)


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
    now = datetime.now()
    # 提前设置好的请求参数
    stock_remind_record = db['stock_remind_record']

    r = stock_remind_record.find({"date":date_util.get_start_of_day(now),"key":key})

    return restful.response(r)


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

    match = {"date": date, "$expr": {"$and": []}}

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
