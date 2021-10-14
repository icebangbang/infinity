import time
import pymysql
from sshtunnel import SSHTunnelForwarder
from other.public import request_method
from app.main.db.mongo import db
from bson import ObjectId


class MI:
    def __init__(self, cursor, sql):
        self.cursor = cursor
        self.sql = sql
        self.latest_id = 0

    def __iter__(self):
        return self

    def __next__(self):
        latest_id = db['temp2'].find_one({"_id": ObjectId("61656102400a8b112afa54c8")})['id']
        sql = self.sql.format(latest_id)
        self.cursor.execute(sql)
        r = self.cursor.fetchall()
        return r


with SSHTunnelForwarder(
        ("52.184.8.192", 3007),
        ssh_username="lifeng.ye",
        ssh_pkey="~/Work/pem/baipeng.pem",
        remote_bind_address=("rm-k1as78x4dp90382jt.mysql.ap-southeast-5.rds.aliyuncs.com", 3306),
        local_bind_address=("0.0.0.0", 1022)
) as tunnel:
    conn_rum = pymysql.Connect(
        host='127.0.0.1',
        port=tunnel.local_bind_port,
        user='tropic', passwd='5pdUNJBoBW#GZldg',
        db='rum', charset='utf8',
        cursorclass=pymysql.cursors.DictCursor)

    cursor_rum = conn_rum.cursor()

    sql = "select id,thirdparty_order_id from ks_loan_order where id > {} and thirdparty_order_id is not null and partner_code = 'mautunai' and status>=100 limit 100"

    m = MI(cursor_rum, sql)
    for i in m:
        for item in i:
            thirdparty_order_id = item['thirdparty_order_id']
            detail = request_method(thirdparty_order_id)
            id = detail['data']['apply_list'][0]['_id']
            index = item['id']
            db['temp'].insert_one(dict(thirdparty_order_id=thirdparty_order_id, id=id))

            db['temp2'].update_one({"_id": ObjectId("61656102400a8b112afa54c8")}, {"$set": {"id": index}})
            print(id)
