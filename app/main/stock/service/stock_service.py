import logging
from datetime import datetime, timedelta
import pandas as pd

from app.main.stock import constant
from app.main.stock.dao import stock_dao, k_line_dao
from app.main.stock.stock_pick_filter import stock_filter
from app.main.utils import date_util
from app.main.stock.stock_kline import id_map
from app.main.stock.service import search_udf_service, stock_search_service
import akshare as ak
from app.main.db.mongo import db
from app.main.stock.task_wrapper import TaskWrapper
import json
from app.main.utils import dingtalk_util
import time


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


def stock_remind():
    query_store = db["ind_query_store"]
    query_list = list(query_store.find({"in_use": 1}))
    # name,params
    for query in query_list:
        name = query['name']  # 指标集名称
        msg_template = query['msg_template']
        request_body = json.loads(query['body'])
        request_body['date'] = '2022-04-29'

        result = stock_search_service.comprehensive_search(request_body)
        if result['size'] == 0: return
        board_counter = result['counter']
        boards_in_front = list(board_counter.keys())[0:10]
        boards_in_front_fmt = []

        msg = '提醒-------------------------开始一轮推送--------------------------'
        dingtalk_util.send_msg(msg)

        for board in boards_in_front:
            count = board_counter[board]
            content = "{}({})".format(board, count)
            boards_in_front_fmt.append(content)
        msg = '[板块提醒]前十板块:{}'.format(",".join(boards_in_front_fmt))

        dingtalk_util.send_msg(msg)
        for board in boards_in_front:
            stock_detail_list = result['detail']
            stocks_in_front = []
            count = 0
            for stock_detail in stock_detail_list:
                if count >= 10:
                    break

                boards_of_stock = stock_detail['boards']
                if board in boards_of_stock:
                    stocks_in_front.append("{}({})".format(stock_detail['name'],stock_detail['rate']))
                    count = count + 1
            msg = '[个股提醒]{}前十个股:{}'.format(board, ",".join(stocks_in_front[0:10]))
            time.sleep(6)
            resp = dingtalk_util.send_msg(msg)

        msg = '提醒-------------------------结束一轮推送--------------------------'
        dingtalk_util.send_msg(msg)

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


if __name__ == "__main__":
    # stocks = stock_dao.get_all_stock(dict(code=1))
    # code_name_map = stock_dao.get_code_name_map()
    # to_time = datetime.now()
    # from_time = to_time - timedelta(739)
    # stock_filter.get_stock_status(from_time, to_time)
    # publish(3, 100)
    stock_remind()
    msg = "提醒:{stock_code}[{code}]在出现底部反转{inf_l_point_value}[{inf_l_point_date}],当前价格突破前期小高位{current_max_high_type},"

    # d = {"stock_code": "1", "code": "2",
    #         "inf_l_point_value": "3", "inf_l_point_date": "4",
    #         "inf_h_point_value": "5","inf_h_point_date":"6",
    #         }
    # print(msg.format(**d))

    # stock_value_set = db["stock_value"]
    # stock_value_set.update_one({"code": "300763", "date": datetime.now()},
    #                            {"$set": dict(
    #                                MarketValue=0,
    #                                flowCapitalValue=0,
    #                                update_time=datetime.now()),
    #                            }, True)
