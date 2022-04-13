import logging
from datetime import datetime, timedelta

import pandas as pd

from app.main.stock import constant
from app.main.stock.dao import stock_dao, k_line_dao
from app.main.stock.stock_pick_filter import stock_filter
from app.main.utils import date_util
from app.main.stock.stock_kline import id_map
import akshare as ak
from app.main.db.mongo import db
from app.main.stock.task_wrapper import TaskWrapper
import requests


def publish(days=10, slice=30, code_list=None, stock_map={}, start=None, end=None):
    if start is None and end is None:
        end = date_util.get_start_of_day(datetime.now())
        start, end = date_util.get_work_day(end, offset=days)

    if code_list is None:
        stocks = stock_dao.get_all_stock()
    else:
        stocks = stock_dao.get_stock_detail_list(code_list)

    rise = []
    result_dict = dict()
    name_dict = dict()
    for stock in stocks:
        name_dict[stock['code']] = stock['name']

    page_size = 200
    start_index = 0
    end_index = page_size
    flag = False

    while flag is False:
        logging.info("current index is {}".format(start_index))
        if end_index < len(stocks):
            inner = stocks[start_index:end_index]
            start_index = end_index
            end_index = end_index + page_size
        else:
            inner = stocks[start_index:]
            flag = True
        temp_code_list = [item['code'] for item in inner]
        result_dict = {item['code']: [] for item in inner}
        k_list = k_line_dao.get_k_line_by_code(temp_code_list, start, end)
        for k in k_list:
            result_dict[k['code']].append(k)
        for k, v in result_dict.items():
            if len(v) > 0:
                if len(v) == 1:
                    earliest = v[0]["open"]
                    latest = v[0]["close"]
                    c = (latest - earliest) / earliest
                else:
                    if v[0]['code'] == '300882':
                        print(123)
                    earliest = v[0]["close"]
                    latest = v[-1:][0]["close"]
                    c = (latest - earliest) / earliest
                rise.append((k, name_dict[k], c))
        result_dict.clear()

    rise = pd.DataFrame(rise)
    rise.columns = ['code', 'name', 'rise']
    rise = rise.sort_values(by='rise', ascending=False)
    new = rise.to_dict("records")

    top = new[0:slice]

    rise = rise.sort_values(by='rise', ascending=True)
    new = rise.to_dict("records")

    bot = new[0:slice]

    print("涨幅前{}是:".format(slice))
    for i in top:
        print("{} {} {} {}".format(i['code'], i['name'], round(i['rise'] * 100, 3), get_concepts(stock_map, i['code'])))

    print("跌幅前{}是:".format(slice))
    for i in bot:
        print("{} {} {} {}".format(i['code'], i['name'], round(i['rise'] * 100, 3), get_concepts(stock_map, i['code'])))


def get_concepts(stock_map, code):
    if code in stock_map.keys():
        return stock_map[code]['board']
    return ""


def sync_stock_ind(codes, task_wrapper: TaskWrapper = None):
    stock_detail_set = db["stock_detail"]
    stock_value_set = db["stock_value"]
    print("code size {}".format(len(codes)))
    for code in codes:
        now = datetime.now()
        # start_of_day = date_util.get_start_of_day(now)
        k_line_data_list = k_line_dao.get_k_line_by_code([code], limit=1, sort=-1)
        df = ak.stock_ind(code, id_map)
        ind_dict = df.to_dict("records")[0]
        ind_dict['MarketValue'] = round(ind_dict['MarketValue'] / 100000000, 2)
        ind_dict['flowCapitalValue'] = round(ind_dict['flowCapitalValue'] / 100000000, 2)
        ind_dict['update_time'] = now
        stock_detail_set.update_one({"code": code}, {"$set": ind_dict})

        stock_value_set.update_one({"code": code, "date": k_line_data_list[0]['date']},
                                   {"$set": dict(
                                       MarketValue=ind_dict['MarketValue'],
                                       flowCapitalValue=ind_dict['flowCapitalValue'],
                                       update_time=now),
                                   }, upsert=True)

        if task_wrapper is not None:
            task_wrapper.trigger_count()


def stock_search(params):
    stock_feature = db['stock_feature']

    date = date_util.parse_date_time(params.get("date"), fmt="%Y-%m-%d")
    date = date if date is not None else date_util.get_start_of_day(datetime.now())
    match = {"date": date, "$expr": {"$and": []}}

    key_list: list = constant.get_feature_keys()
    # 查看用户自定义的参数是否在特征列表中
    for name in params.keys():
        if name not in key_list: continue
        # 参数筛选表达式
        condition = params[name]
        # condition[0]: 表达式 $gt,$lt,$eq诸如此类
        # condition[1]: 所要过滤的值
        """
        condition[1]有几种类型:
        1. float or int
        2. {"$multiply": ["$features.vol_avg_5", 10]}  放量特征筛选
        3. $features.ma30 特征自身比较
        4. 时间字符串
        """
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


def stock_remind():
    query_store = db["ind_query_store"]
    query_list = list(query_store.find({}))
    # name,params
    for query in query_list:
        name = query['name']  # 指标集名称
        param = query['params']

        stocks = stock_search(param)
        msg = ''
        for stock in stocks:
            content = "提醒:{}[{}]在出现底部反转{}[{}],当前价格突破前期高位反转点{}[{}],"

            inf_l_point_date = stock['features']['inf_l_point_date']
            inf_l_point_value = stock['features']['inf_l_point_value']
            inf_h_point_date = stock['features']['inf_h_point_date']
            inf_h_point_value = stock['features']['inf_h_point_value']
            name = stock['name']
            stock_code = stock['stock_code']
            msg = msg + content.format(stock_code, name,
                                       inf_l_point_value, date_util.dt_to_str(inf_l_point_date),
                                       inf_h_point_value, date_util.dt_to_str(inf_h_point_date)) + '\n'

        headers = {'Content-Type': 'application/json'}
        d = {"msgtype": "text",
             "text": {
                 "content": msg
             }}
        requests.post(
            "https://oapi.dingtalk.com/robot/send?access_token=8d6107691edc8c68957ad9b3b3e16eeccf4fd2ec005c86692fdeb648da6312b4",
            json=d, headers=headers)


if __name__ == "__main__":
    # stocks = stock_dao.get_all_stock(dict(code=1))
    # code_name_map = stock_dao.get_code_name_map()
    # to_time = datetime.now()
    # from_time = to_time - timedelta(739)
    # stock_filter.get_stock_status(from_time, to_time)
    # publish(3, 100)

    stock_value_set = db["stock_value"]
    stock_value_set.update_one({"code": "300763", "date": datetime.now()},
                               {"$set": dict(
                                   MarketValue=0,
                                   flowCapitalValue=0,
                                   update_time=datetime.now()),
                               }, True)
