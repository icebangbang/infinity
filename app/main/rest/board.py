import collections
from typing import List

from app.main.stock.const import board_const
from app.main.stock.dao import k_line_dao
from app.main.utils import restful, date_util
from . import rest
from app.main.task import demo
from app.main.task import board_task
from app.main.db.mongo import db
import pandas as  pd
from datetime import timedelta, datetime
from flask import request
import re

@rest.route("/board/list/custom", methods=['get'])
def get_custom_board_list():
    config = db['config']
    board_info = config.find_one({"name": "board"}, {"_id": 0})
    board_custom = board_info['value']

    set = db['board_detail']
    condition = {"$or": [{"type": 2}, {"board": {"$in": board_custom}}]}
    boards = set.find(condition, dict(board=1, _id=0))
    results = [ board['board'] for board in boards]

    return restful.response(results)

@rest.route("/board/list", methods=['get'])
def get_board_list():
    set = db['board_detail']
    condition = {"$or": [{"type": 2}, {"board": {"$in": board_const.include}}]}
    boards = list(set.find(condition,dict(board=1, _id=0)))

    return restful.response(boards)


@rest.route("/board/rank", methods=['get'])
def get_board():
    set = db["board_k_line_day"]
    board_type = int(request.args.get("type", 2))

    latest = set.find_one({}, sort=[("date", -1)])
    date = latest['date']

    total = list(set.find({"date": {"$lte": date, "$gte": date - timedelta(days=1)}, "type": board_type}))

    df_total = pd.DataFrame(total)

    results = []
    for name, group in df_total.groupby("name"):
        latest_close = None
        first_close = None
        item = None

        if len(group) != 1:
            i = 0
            for index, line in group.iterrows():
                if i == 0:
                    first_close = line['close']
                if i == len(group) - 1:
                    latest_close = line['close']
                i = i + 1
            inc_rate = round((latest_close - first_close) / first_close * 100, 2)
            item = dict(name=name, rate=inc_rate)
        else:
            line = group.iloc[0]
            inc_rate = round((line['close'] - line['open']) / line['open'] * 100, 2)

            item = dict(name=name, rate=inc_rate)
        results.append(item)

    results = sorted(results, key=lambda x: x['rate'], reverse=True)

    return restful.response(results)


@rest.route("/board/data/miner", methods=['post'])
def board_miner():
    params: dict = request.json
    results = get_board_result(params)
    names = [r['name'] for r in results]

    start = date_util.parse_date_time(params.get("date"), "%Y-%m-%d")
    end = date_util.parse_date_time(params.get("until"), "%Y-%m-%d")

    # if date_util.get_days_between(end, start) == 0:
    start = date_util.get_work_day(start, 1)
    # start = start - timedelta(days=1)

    datas = k_line_dao.get_board_k_line_by_name(names, start, end)
    group = {}
    for data in datas:
        code = data['name']
        array = group.get(code, [])
        array.append(data)
        group[code] = array

    final = {}

    boards = []
    for result in results:
        name = result['name']

        trade_data_list = group[name]

        close_list = [trade_data['close'] for trade_data in trade_data_list]

        a = close_list[0]
        b = max(close_list[1:]) if len(close_list) > 1 else a
        index = close_list.index(b)
        high_date = trade_data_list[index]['date']
        rate = round((b - a) / a * 100, 2)

        final[name] = dict(
            rate=rate,
            high_date=high_date,
        )

    counter = collections.Counter(boards)
    final = collections.OrderedDict(sorted(final.items(), key=lambda item: item[1]['rate'], reverse=True))

    return restful.response(dict(counter=dict(counter.most_common(20)),
                                 detail=final, size=len(final)))


def get_board_result(params) -> List[dict]:
    stock_feature = db['board_feature']

    date = date_util.parse_date_time(params.get("date"), fmt="%Y-%m-%d")
    date = date if date is not None else date_util.get_start_of_day(datetime.now())
    gap = params.get("gap", None)
    up_shadow_rate = params.get("up_shadow_rate", None)
    rate = params.get("rate", None)  # ["$eq",0]
    close_rate_5 = params.get("close_rate_5", None)  # ["$eq",0]
    entity_length = params.get("entityLength", None)  # ["$gt",0] k线实体
    sma_down = params.get("smaDown", None)  # 均线空头
    sma_up = params.get("smaUp", None)  # 均线空头
    volume_up_10 = params.get("volumeUp10", None)
    volume_up_5 = params.get("volumeUp5", None)
    volume_down_5 = params.get("volumeDown5", None)

    match = {"date": date, "$expr": {"$and": []},"name":{
        "$not": {
            "$in": ['融资融券', '富时罗素', '标准普尔',
                    '深股通', 'MSCI中国', '沪股通', '深成500',
                    '创业板综', '中证500', '上证380', '转债标的', '内贸流通', '电商概念', '机构重仓',
                    re.compile("板块$")]}
    }}

    if volume_up_10 is not None:
        match["$expr"]["$and"].append(
            {"$gte": ["$features.volume", {"$multiply": ["$features.vol_avg_10", volume_up_10]}
                      ]})
    if volume_up_5 is not None:
        match["$expr"]["$and"].append({"$gte": ["$features.volume", {"$multiply": ["$features.vol_avg_5", volume_up_5]}
                                                ]})

    if volume_down_5 is not None:
        match["$expr"]["$and"].append({"$lt": ["$features.volume", {"$multiply": ["$features.vol_avg_5", volume_down_5]}
                                               ]})

    if gap is not None:
        match["$expr"]["features.gap"] = {"$in": gap}

    if up_shadow_rate is not None:
        pass

    if rate is not None:
        match["$expr"]["$and"].append({rate[0]: ["$features.rate", rate[1]]})

    if close_rate_5 is not None:
        match["$expr"]["$and"].append({close_rate_5[0]: ["$features.close_rate_5", close_rate_5[1]]})

    if entity_length is not None:
        match["$expr"]["$and"].append({entity_length[0]: ["$features.entity_length", entity_length[1]]})

    if sma_down:
        match["$expr"]["$and"].append({"$gte": ["$features.ma60", "$features.ma30"]})
        match["$expr"]["$and"].append({"$gte": ["$features.ma30", "$features.ma20"]})
        match["$expr"]["$and"].append({"$gte": ["$features.ma20", "$features.ma10"]})
    if sma_up:
        match["$expr"]["$and"].append({"$lte": ["$features.ma60", "$features.ma30"]})
        match["$expr"]["$and"].append({"$lte": ["$features.ma30", "$features.ma20"]})
        match["$expr"]["$and"].append({"$lte": ["$features.ma20", "$features.ma10"]})
        match["$expr"]["$and"].append({"$lte": ["$features.ma10", "$features.ma5"]})

    condition = stock_feature.find(match)
    results = list(condition)
    return results
