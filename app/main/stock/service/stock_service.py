import logging
from datetime import datetime
from decimal import Decimal

import pandas as pd

from app.main.stock.api import stock_info
from app.main.utils import my_redis

from app.main.stock.dao import stock_dao, k_line_dao, index_dao
from app.main.utils import date_util
from app.main.stock.api.stock_kline import id_map
from app.main.stock.service import stock_search_service
import akshare as ak
from app.main.db.mongo import db
from app.main.stock.task_wrapper import TaskWrapper
import json


def publish(days=10, slice=30, code_list=None, stock_map={}, start=None, end=None):
    if start is None and end is None:
        end = date_util.get_start_of_day(datetime.now())
        start = date_util.get_work_day(end, offset=days)

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
        print(code)
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

        # if task_wrapper is not None:
        #     task_wrapper.trigger_count()


def stock_remind():
    now = datetime.now()
    if now.hour >= 16:
        return
    if date_util.is_workday(now) is False or date_util.is_weekend(now):
        return

    query_store = db["ind_query_store"]
    query_list = list(query_store.find({"in_use": 1}))
    day_span = 5
    # name,params
    matched_result = {}
    for query in query_list:
        result = {}
        name = query['name']  # 指标集名称
        key = query['key']  # 指标集名称

        request_body = json.loads(query['body'])
        origin_date = request_body['date']
        origin_until = request_body['until']
        start = date_util.get_work_day(datetime.now(), day_span + 1)
        latest_day = date_util.get_work_day(now, 1)
        # 回溯前几天的行情概览,将出现的板块加入缓存中

        latest_boards = None
        my_redis.delete("good_board_in_history")
        # latest_boards = my_redis.hget("good_board_in_history", date_util.date_time_to_str(start, "%Y-%m-%d"), )

        if latest_boards is None:
            base = start
            for i in range(day_span):
                base = date_util.add_and_get_work_day(base, 1)
                dt = date_util.date_time_to_str(base, "%Y-%m-%d")
                request_body['date'] = dt
                request_body['until'] = dt
                result = stock_search_service.comprehensive_search(request_body)
                board_counter = result['counter']
                boards_in_front = list(board_counter.keys())[0:20]
                my_redis.hset("good_board_in_history", dt, json.dumps(boards_in_front, ensure_ascii=False))
                # n 天过期
                my_redis.expire("good_board_in_history", day_span * 24 * 60 * 60)

        request_body['date'] = origin_date
        request_body['until'] = origin_until
        result = stock_search_service.comprehensive_search(request_body)
        if result['size'] == 0: return
        board_counter = result['counter']
        boards_in_front = list(board_counter.keys())[0:20]
        boards_in_front_fmt = []

        matched_result["name"] = name
        matched_result["key"] = key

        # msg = '提醒-------------------------开始一轮推送--------------------------'
        # dingtalk_util.send_msg(msg)
        board_dict = {}
        for board in boards_in_front:
            in_time = 1
            base = start
            for i in range(day_span):
                base = date_util.add_and_get_work_day(base, 1)
                boards_json = my_redis.hget("good_board_in_history",
                                            date_util.date_time_to_str(base, "%Y-%m-%d"))
                boards_of_history = json.loads(boards_json)
                if board in boards_of_history:
                    in_time = in_time + 1
            count = board_counter[board]
            content = "{}({})({})".format(board, count, in_time)
            board_dict[board] = dict(board=board, count=count, inTime=in_time)
            boards_in_front_fmt.append(content)
        msg = '[板块提醒]前二十板块:{}'.format(",".join(boards_in_front_fmt))

        # dingtalk_util.send_msg(msg)
        for board in boards_in_front:
            board_dict[board]['stocks'] = []
            stock_detail_list = result['detail']
            stocks_in_front = []
            count = 0
            # 历史出现次数
            in_time = 0
            for stock_detail in stock_detail_list:
                # if count >= 10:
                #     break

                boards_of_stock = stock_detail['boards']
                if board in boards_of_stock:
                    # count = count + 1
                    stocks_in_front.append("{}({})".format(stock_detail['name'], stock_detail['rate']))
                    board_dict[board]['stocks'].append(
                        dict(name=stock_detail['name'], rate=stock_detail['rate'], money=stock_detail['money_median']))

            msg = '[个股提醒]{}前十个股:{}'.format(board, ",".join(stocks_in_front[0:10]))
            # time.sleep(3.5)
            # resp = dingtalk_util.send_msg(msg)

        matched_result["boards"] = list(board_dict.values())
        matched_result["date"] = date_util.get_start_of_day(now)
        matched_result["update"] = now

        msg = '提醒-------------------------结束一轮推送--------------------------'
        # dingtalk_util.send_msg(msg)

        stock_remind_record = db["stock_remind_record"]
        stock_remind_record.update_one({"date": date_util.get_start_of_day(now)}, {"$set": matched_result}, upsert=True)
        # for stock in stocks:
        #
        #     # name = stock['name']
        #     # stock_code = stock['stock_code']
        #     features = stock['features']
        #     features['stock_code'] = stock['stock_code']
        #     features['name'] = stock['name']
        #     msg = msg + msg_template.format(**stock['features']) + '\n'
        #
        # headers = {'Content-Type': 'application/json'}
        # d = {"msgtype": "text",
        #      "text": {
        #          "content": msg
        #      }}
        # requests.post(
        #     "https://oapi.dingtalk.com/robot/send?access_token=8d6107691edc8c68957ad9b3b3e16eeccf4fd2ec005c86692fdeb648da6312b4",
        #     json=d, headers=headers)


def stock_remind_v2():
    """
    筛选个股结果存储
    :return:
    """
    now = datetime.now()
    # now = datetime(2022, 8, 12)
    # if now.hour >= 22:
    #     return
    # if date_util.is_workday(now) is False or date_util.is_weekend(now):
    #     return

    query_store = db["ind_query_store"]
    query_list = list(query_store.find({"in_use": 1}))
    day_span = 20
    # name,params
    matched_result = {}
    for query in query_list:
        result = {}
        name = query['name']  # 指标集名称
        key = query['key']  # 指标集名称

        request_body = json.loads(query['body'])
        origin_date = request_body['date']
        origin_until = request_body['until']
        start = date_util.get_work_day(datetime.now(), day_span + 1)
        latest_day = date_util.get_work_day(now, 1)
        # 回溯前几天的行情概览,将出现的板块加入缓存中

        latest_results = my_redis.hget_all("good_board_in_history2")
        data_of_yesterday = date_util.add_and_get_work_day(now, 1)

        if my_redis.hget("good_board_in_history2",
                         date_util.date_time_to_str(data_of_yesterday, "%Y-%m-%d")) is None:
            base = start
            my_redis.delete("good_board_in_history2")
            for i in range(day_span):
                base = date_util.add_and_get_work_day(base, 1)
                dt = date_util.date_time_to_str(base, "%Y-%m-%d")
                request_body['date'] = dt
                request_body['until'] = dt
                result = stock_search_service.comprehensive_search(request_body)
                # board_counter = result['counter']
                # boards_in_front = list(board_counter.keys())[0:15]
                my_redis.hset("good_board_in_history2", dt, json.dumps(result, ensure_ascii=False))
                # # n 天过期
                # my_redis.expire("good_board_in_history2", day_span * 24 * 60 * 60 * 1000)

        request_body['date'] = origin_date
        request_body['until'] = origin_until
        result = stock_search_service.comprehensive_search(request_body)
        if result['size'] == 0: return
        board_counter = result['counter']
        boards_in_front = list(board_counter.keys())[0:15]

        matched_result["name"] = name
        matched_result["key"] = key

        # 需要展示的板块
        board_dict = {}
        for board in boards_in_front:
            in_time = 1
            base = start
            stocks_set = set()
            for i in range(day_span):
                base = date_util.add_and_get_work_day(base, 1)
                # 历史搜索结果
                search_result_json = my_redis.hget("good_board_in_history2",
                                                   date_util.date_time_to_str(base, "%Y-%m-%d"))
                if search_result_json is None:
                    print(123)
                search_result = json.loads(search_result_json)
                history_counter = search_result['counter']

                stock_detail_list_history = [stock['name'] for stock in search_result['detail'] if
                                             stock['industry'] == board]
                # 历史前20天命中的个股的结果
                stocks_set.update(stock_detail_list_history)

                # 排名前列的板块
                front = list(history_counter.keys())[0:15]
                if board in front:
                    in_time = in_time + 1

            count = board_counter[board]
            board_dict[board] = dict(board=board, count=count, inTime=in_time, stocks=[],
                                     historyStocks=list(stocks_set))

        stock_detail_list = result['detail']

        for stock_detail in stock_detail_list:
            industry = stock_detail['industry']
            if industry in board_dict.keys():
                board_dict[industry]['stocks'].append(
                    dict(name=stock_detail['name'], rate=stock_detail['rate'], money=stock_detail['money_median']))
        matched_result["boards"] = list(board_dict.values())
        matched_result["date"] = date_util.get_start_of_day(now)
        matched_result["update"] = now
        stock_remind_record = db["stock_remind_record"]
        stock_remind_record.update_one({"date": date_util.get_start_of_day(now), "key": key}, {"$set": matched_result},
                                       upsert=True)


def cal_stock_deviation(code, offset_day):
    """
    计算个股n日内偏离值
    :param code:
    :param offset_day: n日内偏离
    :return:
    """
    now = datetime.now()
    start_time = date_util.get_start_of_day(now)
    k_line_list = k_line_dao.get_k_line_data_by_offset(start_time, -offset_day, code=code, reverse_result=False)
    deviation_value = 0

    result = {}
    for index, k_line in enumerate(k_line_list):
        close = k_line['close']
        prev_close = k_line['prev_close']
        rate = Decimal((close - prev_close) / prev_close * 100).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")

        index_k_line = index_dao.get_index_data_by_offset(k_line['date'], -1, 'day', "399106")[0]

        index_close = index_k_line['close']
        index_prev_close = index_k_line['prev_close']
        index_rate = Decimal((index_close - index_prev_close) / index_prev_close * 100).quantize(Decimal("0.01"),
                                                                                                 rounding="ROUND_HALF_UP")

        current_day_deviation = rate - index_rate
        deviation_value = current_day_deviation + deviation_value

        if index == len(k_line_list) - 2:
            result['近{}日偏离值'.format(index + 1)] = deviation_value
    result['近{}日偏离值'.format(offset_day)] = deviation_value

    return result


def sync_bellwether():
    """
    同步行业板块领头羊数据
    :return:
    """
    data_list = ak.get_bellwether()
    for data in data_list:
        data['date'] = date_util.get_start_of_day(datetime.now())
        data['update'] = datetime.now()

    special_stock = db['special_stock']
    for data in data_list:
        special_stock.update_one(dict(industry=data['industry'], date=data['date']), {"$set": data}, upsert=True)


def get_full_stock_detail(name):
    """
    组合个股的详细情况
    :return:
    """
    detail = {}
    # 个股详情
    # stock_detail = stock_dao.get_stock_detail_by_code(code)
    stock_detail = stock_dao.get_stock_detail_by_name(name)
    # 获取近30日k线图
    now = date_util.get_latest_work_day()
    code = stock_detail['code']
    k_line_data = k_line_dao.get_k_line_data_by_offset(now, -30, code=stock_detail['code'])

    x = [date_util.date_time_to_str(data['date'], "%Y-%m-%d") for data in k_line_data]
    y = [[data['open'], data['close'], data['low'], data['high'], 1] for data in k_line_data]

    high_list = [data['high'] for data in k_line_data]
    low_list = [data['low'] for data in k_line_data]

    # stock_feature
    stock_business = stock_info.get_stock_business(stock_detail)

    features = stock_dao.get_company_feature(code, now)

    # 涨幅中位数
    up_median = features['up_median']
    # 跌幅中位数
    down_median = features['down_median']

    detail['up_median'] = up_median
    detail['down_median'] = down_median
    detail['stock_business'] = stock_business
    detail['code'] = code

    detail['option'] = dict(
        grid={
            "top": "0px",
            "left": "0px",
            "right": "0px",
            "bottom": '0px',
        },
        xAxis={
            "show": True,
            "data": x
        },
        yAxis={
            "max": max(high_list),
            "min": min(low_list),
            "show": True,
        },
        series=[
            {
                "type": 'candlestick',
                "data": y}
        ]
    )

    return detail


if __name__ == "__main__":
    # stocks = stock_dao.get_all_stock(dict(code=1))
    # code_name_map = stock_dao.get_code_name_map()
    # to_time = datetime.now()
    # from_time = to_time - timedelta(739)
    # stock_filter.get_stock_status(from_time, to_time)
    # publish(3, 100)
    # stock_remind_v2()
    # detail = get_full_stock_detail("300763")
    pass
    # sync_bellwether()
    # stock_remind()
    # cal_stock_offset("000722",10)

    # d = {"stock_code": "1", "code": "2",
    #         "inf_l_point_value": "3", "inf_l_point_date": "4",
    #         "inf_h_point_value": "5","inf_h_point_date":"6",
    #         }
    # print(msg.format(**d))
    sync_stock_ind(["300763"])
    # stock_value_set = db["stock_value"]
    # stock_value_set.update_one({"code": "300763", "date": datetime.now()},
    #                            {"$set": dict(
    #                                MarketValue=0,
    #                                flowCapitalValue=0,
    #                                update_time=datetime.now()),
    #                            }, True)
