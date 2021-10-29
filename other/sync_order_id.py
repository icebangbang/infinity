import pymysql
from sshtunnel import SSHTunnelForwarder
from other.public import request_method
from app.main.db.mongo import db
from other.snowflake import get_guid

# 生产环境

with SSHTunnelForwarder(
        ("52.184.8.192", 3007),
        ssh_username="lifeng.ye",
        ssh_pkey="~/Work/pem/baipeng.pem",
        remote_bind_address=("rm-k1as78x4dp90382jt.mysql.ap-southeast-5.rds.aliyuncs.com", 3306),
        local_bind_address=("0.0.0.0", 1022)
) as tunnel:
    conn_sake = pymysql.Connect(
        host='127.0.0.1',
        port=tunnel.local_bind_port,
        user='tropic', passwd='5pdUNJBoBW#GZldg',
        db='sake', charset='utf8',
        cursorclass=pymysql.cursors.DictCursor)

    cursor_sake = conn_sake.cursor()

# conn_sake = pymysql.Connect(
#     host='120.55.200.28',
#     port=3306,
#     user='ecreditpal', passwd='vaiFA3MQ9dLcDjWL',
#     db='sake', charset='utf8',
#     cursorclass=pymysql.cursors.DictCursor)

    # cursor_sake = conn_sake.cursor()

    # cursor_sake.execute("select * from bid where saas_id=2237")
    # bids = cursor_sake.fetchall()

    # for index,bid in enumerate(bids):
        # cursor_sake.execute("select * from bankcard where saas_id=2237 and user_id = {}".format(bid['user_id']))
        # bankcard = cursor_sake.fetchone()
        #
        # bank_account_number = bankcard['bank_account_number']
        # bank_account_id = bankcard['id']
        # amount = float(bid['amount']) * 0.65
        # bid_id = bid['id']
        # mobile = bid['mobile']
        # deduct_time = bid['deduct_time']
        #
        #
        # payment_record_id = get_guid()
        # insert_payment_record_sql = "INSERT INTO `sake`.`payment_record`(`id`, `type`, `bank_account`, `bank_id`, `amount`, `status`, `bid_id`, `mobile`, `saas_id`, `channel_id`, `payment_channel`, `notify_time`) " \
        #                             "VALUES ({}, 3, '{}', {}, {}, 1, {}, '{}', 2237, 2, 'flinpay', '{}');".format(
        #     payment_record_id, bank_account_number, bank_account_id, amount, bid_id, mobile, deduct_time
        # ).replace("'None',", "null,").replace("None,", "null,")
        #
        # cursor_sake.execute(insert_payment_record_sql)
        # conn_sake.commit()
        #
        # print(index)


    #
    all = list(db['tempx'].find({}))

    for index,a in enumerate(all):
        if index < 12324: continue
        t = a['thirdparty_order_id']
        id = a['id']

        bid_sql = "update bid set other_order_id='{}' where contract_no='{}'".format(id,t)
        # bill_sql = "update bill set other_order_id='{}' where contract_no='{}'".format(id,t)

        print(index)
        print(t,id,cursor_sake.execute(bid_sql))
        # print(t,id,cursor_sake.execute(bill_sql))
        conn_sake.commit()
