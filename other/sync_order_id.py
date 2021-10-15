import pymysql
from sshtunnel import SSHTunnelForwarder
from other.public import request_method

# 生产环境

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

    conn_sake = pymysql.Connect(
        host='127.0.0.1',  # 测试环境
        port=tunnel.local_bind_port,
        user='tropic', passwd='5pdUNJBoBW#GZldg',
        db='rum', charset='utf8',
        cursorclass=pymysql.cursors.DictCursor)
    cursor_rum = conn_sake.cursor()

    sql = ""

