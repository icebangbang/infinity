import collections
from collections import OrderedDict
from datetime import datetime

from app.main.db.mongo import db
from app.main.stock import constant
from app.main.stock.dao import k_line_dao
from app.main.stock.service import search_udf_service
from app.main.utils import date_util, restful, simple_util


def comprehensive_search(request_body):
    """
    结合板块搜索
    :param request_body:
    :param request:
    :return:
    """
    # 处理一下入参
    request_body = search_udf_service.check_and_parse(request_body)
    # 数据库检索
    results: list = stock_search(request_body)
    codes = [r['stock_code'] for r in results]

    aim_board = request_body['custom'].get("aimBoard", None)
    only_cyb = request_body['custom'].get("onlyCyb", False)
    hide_board = request_body['custom'].get("hideBoard", False)
    only_code = request_body['custom'].get("onlyCode", False)

    start = date_util.parse_date_time(request_body.get("date"), "%Y-%m-%d")
    end = date_util.parse_date_time(request_body.get("until"), "%Y-%m-%d")

    start, useless = date_util.get_work_day(start, 1)

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

            elif board not in ['融资融券', '富时罗素', '标准普尔', '预盈预增',
                               '昨日涨停_含一字', '昨日涨停', '预亏预减','深股通',
                               'MSCI中国', '沪股通', '深成500','预亏预减', '深股通',
                               '创业板综','创业板综', '中证500', '上证380', '转债标的',
                               '内贸流通', '电商概念', '机构重仓', 'QFII重仓', '长江三角',
                               '基金重仓','HS300_','国企改革','股权激励','证金持股',
                               '深圳特区','创业成分','百元股','次新股','注册制次新股']:

                boards.append(board)
        if code not in group.keys(): continue
        if simple_util.is_not_empty(aim_board) and aim_board not in board_list: continue

        if only_cyb and code.startswith("300") is False: continue

        trade_data_list = group[code]
        #
        close_list = [trade_data['close'] for trade_data in trade_data_list]

        a = close_list[0]
        b = max(close_list[1:]) if len(close_list) > 1 else a
        index = close_list.index(b)
        high_date = trade_data_list[index]['date']
        rate = result['features']['rate']

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
        return list(final.keys())
    else:
        final = [item for item in final.values()]

    return dict(counter=dict(counter.most_common(20)),
                                 area_counter=dict(area_counter.most_common(10)),
                                 detail=final, size=len(final))

def stock_search(request_body):
    """
    指标搜索个股
    :param request_body:
    :return:
    """
    stock_feature = db['stock_feature']
    params = request_body['params']
    # 拷贝一份
    params = params.copy()
    date = date_util.parse_date_time(request_body.get("date"), fmt="%Y-%m-%d")
    date = date if date is not None else date_util.get_start_of_day(datetime.now())
    input = dict(date=date)
    match = {"date": date, "$expr": {"$and": []}}

    key_list: list = constant.get_feature_keys()
    # 查看用户自定义的参数是否在特征列表中
    for item in params:
        name = item['name']
        if name not in key_list: continue
        # 参数筛选表达式
        condition = item['value']
        # condition[0]: 表达式 $gt,$lt,$eq诸如此类
        # condition[1]: 所要过滤的值
        """
        condition[1]有几种类型:
        1. float or int
        2. {"$multiply": ["$features.vol_avg_5", 10]}  放量特征筛选
        3. $features.ma30 特征自身比较
        4. 时间字符串
        """
        condition[1] = search_udf_service.check(condition[1],input)
        if date_util.is_valid_date(condition[1]):
            condition[1] = date_util.parse_date_time(condition[1], "%Y-%m-%d")
        match["$expr"]["$and"].append({condition[0]: ["$features." + name, condition[1]]})
        match["features." + name] = {"$exists": True}

    condition = stock_feature.aggregate([
        {"$match": match},
        # stock_feature 和  stock_detail根据code join
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