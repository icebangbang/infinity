import requests
import json

from other.snowflake import get_guid
proxies = {
    "http": None,
    "https": None,
}

session = requests.Session()
session.trust_env = False

from app.main.utils import date_util


def convert_status(source_status):
    if source_status == 100:
        return 100
    elif source_status == 121:
        return 170
    elif source_status == 131:
        return 180
    elif source_status == 132:
        return 171
    else:
        return 200

def transferContent(content):
    if content is None:
        return None
    else:
        string = ""
        for c in content:
            if c == '"':
                string += '\\\"'
            elif c == "'":
                string += "\\\'"
            elif c == "\\":
                string += "\\\\"
            else:
                string += c
        return string


def cal_overdue_day(create_time, repayment_time):
    return date_util.get_days_between(create_time, repayment_time)

def update_by_id(table,content,conn):
    new = {k:v for k,v in content.items() if k != 'id'}
    sql = 'UPDATE {} SET {} where id={}'.format(table,', '.join('{}=%s'.format(k) for k in new),content['id'])
    cursor = conn.cursor()
    cursor.execute(sql,list(new.values()))
    conn.commit()

def request_method(third_order_id):
    request_url = 'https://api.mautunai.finboat.net/admin/orders/order/detail'
    data_search = {}
    data_search['_id'] = third_order_id
    request_body = json.dumps(data_search)
    headers = {
        'Content-Type': 'application/json',
        'Referer': 'https://mautunai.finboat.net/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'Cookie': 'access_token_cookie=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MzQzNjQ4MjYsIm5iZiI6MTYzNDM2NDgyNiwianRpIjoiMTQ3YzI2YmItMmM5YS00ZmY2LTgyOGEtZWIzYTQ4MzNkMTBjIiwiZXhwIjoxNjM0NDAwODI2LCJpZGVudGl0eSI6eyJ1aWQiOiI2MDQ1ODIyMDJiMzllMTRlZWY5NjE0MTQiLCJuYW1lIjoibWF1dHVuYWkiLCJwZmxhZyI6MCwicm9sZSI6Ilx1N2JhMVx1NzQwNlx1NTQ1OCJ9LCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJjc3JmIjoiNDk2NGUxN2ItZmJkNi00N2I0LTgwYjMtODIzM2NjZWIwZDc3In0.SL9En_lhG8gaiRudha8v_H_s7VY5X8RFZ7GwNBlxRBQ; csrf_access_token=4964e17b-fbd6-47b4-80b3-8233cceb0d77'
    }
    response = requests.post(url=request_url, headers=headers, data=request_body, proxies=proxies)
    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else:
        print('%s request error, %s' % (third_order_id, response.status_code))
    return None


def insert_bill_extension(order_id, conn, cursor_sake, bank_account_num, name, cid, mobile, product_id, bid_id,
                          new_user_id,current_status,update_time,repayment_time,is_reloan,order_type):
    last_repayment_time = None
    extension_index = 0

    if current_status == 132:
        bill_extension_id = get_guid()
        bill_extension_status = convert_status(current_status)
        bill_extension_creat_time = update_time
        bill_extension_repayment_time = repayment_time
        bill_extension_overdue_days = date_util.get_days_between(bill_extension_creat_time,
                                                                 bill_extension_repayment_time)
        repayment_corpus = 1400000
        repayment_amount = 1400000
        waive_amount = 0

        day = 0 if bill_extension_overdue_days <= 0 else bill_extension_overdue_days
        real_repayment_amount = 1400000 * 0.35 + 0.08 * 1400000 * day
        real_repayment_corpus = 0
        overdue_amount = 0.08 * 1400000 * day
        real_pay_overdue_fine = 0.08 * 1400000 * day
        is_extending = 1
        next_repayment_time = date_util.day_incr(bill_extension_repayment_time,
                                                 7) if day <= 0 else date_util.day_incr(
            bill_extension_repayment_time, 7 + day)

    if current_status == 200:
        bill_extension_id = get_guid()
        bill_extension_status = convert_status(current_status)
        bill_extension_creat_time = update_time
        bill_extension_repayment_time = repayment_time
        bill_extension_overdue_days = date_util.get_days_between(bill_extension_creat_time,
                                                                 bill_extension_repayment_time)
        repayment_corpus = 1400000
        repayment_amount = 1400000
        waive_amount = 0
        is_extending = 0

        day = 0 if bill_extension_overdue_days <= 0 else bill_extension_overdue_days
        real_repayment_amount = 1400000 + 0.08 * 1400000 * day
        real_repayment_corpus = 0
        overdue_amount = 0.08 * 1400000 * day
        real_pay_overdue_fine = 0.08 * 1400000 * day

        next_repayment_time = date_util.day_incr(bill_extension_repayment_time,
                                                 7) if day <= 0 else date_util.day_incr(
            bill_extension_repayment_time, 7 + day)

    insert_bill_extension_sql = "INSERT INTO `sake`.`bill_extension`(" \
                                "`id`,`gmt_create`, `gmt_modified`, `bid_id`, `user_id`, " \
                                "`product_id`, `saas_id`, `channel_id`, `status`, " \
                                "`repayment_corpus`, `repayment_amount`, `real_repayment_amount`, `real_repayment_corpus`, " \
                                "`overdue_amount`, `real_pay_overdue_fine`, `current_overdue_days`, `bank_account_number`, " \
                                "`contract_no`, `name`, `cid`, `mobile`, `overdue_day`, `repayment_time`, `is_reloan`,`is_extending`,`order_type`,`next_repayment_time`) " \
                                "VALUES ({}, '{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, '{}', '{}', '{}', '{}', '{}', {}, '{}', {},{},{},'{}');".format(
        bill_extension_id, bill_extension_creat_time, bill_extension_creat_time, bid_id, new_user_id,
        product_id, 2237, 2, bill_extension_status, repayment_corpus, repayment_amount, real_repayment_amount,
        real_repayment_corpus,
        overdue_amount, real_pay_overdue_fine, day, bank_account_num,
        bid_id, transferContent(name), cid, mobile, bill_extension_overdue_days, bill_extension_repayment_time, is_reloan,is_extending,order_type,next_repayment_time
    ).replace("'None',", "null,").replace("None,", "null,")
    cursor_sake.execute(insert_bill_extension_sql)
    conn.commit()
    print(cid + ',' + mobile + '，' + str(bid_id) + ',' + str(
        bill_extension_status) + ', insert bill_extension ok')
