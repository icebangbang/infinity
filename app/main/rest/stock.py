from app.main.stock.api import stock_info
from app.main.stock.dao import stock_dao, k_line_dao
from app.main.stock.service import stock_service, config_service, search_udf_service, stock_search_service
from app.main.utils import restful, date_util, simple_util, cal_util
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


@rest.route("/stock/detail", methods=['get'])
def stock_detail():
    """
    个股详情查询
    """
    code = request.args.get("code")
    name = request.args.get("name")

    detail = None
    if simple_util.is_not_empty(code):
        detail = stock_dao.get_stock_detail_by_code(code)
    if simple_util.is_not_empty(name):
        detail = stock_dao.get_stock_detail_by_name(name)
    if detail is None:
        return restful.response(dict(name="个股不存在"))
    web = stock_info.get_stock_web(detail)
    detail['web'] = web
    if detail.get('custom') is None:
        detail['custom'] = []

    trade_info = stock_info.get_stock_business(detail)
    detail['trade_info'] = trade_info

    return restful.response(detail)


@rest.route("/stock/deviation", methods=['get'])
def offset_cal():
    """
    股市偏离值计算
    """
    code = request.args.get("code")
    result = stock_service.cal_stock_deviation(code, 10)

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
    now = date_util.get_latest_work_day()
    # 提前设置好的请求参数
    stock_remind_record = db['stock_remind_record']
    special_stock = db['special_stock']
    board_detail = db['board_detail']

    dt = date_util.get_start_of_day(now)
    r = stock_remind_record.find_one({"date": dt, "key": key})

    boards = r['boards']
    board_names = [board['board'] for board in boards]
    board_k_line_day = db['board_k_line_day']
    start = date_util.get_work_day(datetime.now(), 30)
    # 获取行业板块所有数据点位
    data_list = list(board_k_line_day.find({"name": {"$in": board_names}, "date": {
        "$gte": start,
        "$lte": datetime.now()
    }}))
    board_detail_list = list(board_detail.find({"board":{"$in":board_names}}))
    stock_data_list = list(special_stock.find({"date":dt}))

    group = simple_util.group(data_list, "name")
    special_stock_group = simple_util.group(stock_data_list,"industry")
    board_detail_group = simple_util.group(board_detail_list,"board")

    for board in boards:
        group_data = group[board['board']]
        bellwether_detail = special_stock_group[board['board']][0]
        board_detail = board_detail_group[board['board']][0]
        # 板块构成
        stock_of_board_size = len(board_detail['codes'])

        data_x = [date_util.date_time_to_str(data['date'], "%Y-%m-%d") for data in group_data]
        y = [[data['open'], data['close'], data['low'], data['high']] for data in group_data]
        high_list = [data['high'] for data in group_data]
        low_list = [data['low'] for data in group_data]

        # 计算比例

        board['hit_rate'] = cal_util.get_rate(len(board['historyStocks']),stock_of_board_size)
        board['bellwether'] = bellwether_detail['bellwether']
        board['bellwether_rate'] = bellwether_detail['bellwether_rate']
        board['option'] = dict(
            xAxis={
                "show": False,
                "data": data_x
            },
            yAxis={
                "max":max(high_list),
                "min":min(low_list),
                "show": False,
            },
            series=[
                {
                    "type": 'candlestick',
                    "data": y}
            ]
        )

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
