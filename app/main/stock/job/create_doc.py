from datetime import datetime

from app.main.db.mongo import db


def list_doc(table_name: list):
    docs = [
        dict(
            table_name="history_task",
            columns=[
                dict(name="global_id", type="str", desc="全局任务id"),
                dict(name="task_name", type="str", desc="任务名"),
                dict(name="is_finished", type="int", desc="是否成功,0未完成1完成"),
                dict(name="create_time", type="datetime", desc="创建时间"),
                dict(name="update_time", type="datetime", desc="更新时间")
            ],
            example=dict(global_id=202302181055,
                         task_name="历史特征跑批",
                         is_finished=1,
                         create_time=datetime(2023, 1, 1),
                         update_time=datetime(2023, 1, 1))
        ),
        dict(
            table_name="history_task_detail",
            columns=[
                dict(name="global_id", type="str", desc="全局任务id"),
                dict(name="task_name", type="str", desc="任务名称"),
                dict(name="date", type="datetime", desc="任务关联日期"),
                dict(name="status", type="int", desc="状态,0未完成,1处理中,2已完成"),
                dict(name="total", type="int", desc="任务总数"),
                dict(name="index", type="int", desc="任务下标"),
                dict(name="create_time", type="datetime"),
                dict(name="update_time", type="datetime")
            ],
            example=dict(global_id=202302181055,
                         task_name="历史特征跑批",
                         date=datetime(2019, 1, 1),
                         status=1,
                         create_time=datetime(2023, 1, 1),
                         update_time=datetime(2023, 1, 1))
        ),
        dict(table_name="search_keyword_index",
             table_comment="关键字索引表",
             columns=[dict(name="keyword", type="str", desc="关键字名称"),
                      dict(name="refs", type="list", desc="关联数据"),
                      dict(name="type", type="str", desc="数据类型"),
                      ]),
        dict(table_name="etf_hold",
             table_comment="etf持仓详情",
             indexes=dict(code_season_idx=[("code", 1), ("season", 1)]),
             columns=[dict(name="code", type="str", desc="个股代码"),
                      dict(name="fund_code", type="str", desc="基金代码"),
                      dict(name="hold_count", type="int", desc="持股数"),
                      dict(name="hold_money", type="int", desc="持仓市值"),
                      dict(name="name", type="int", desc="个股名称"),
                      dict(name="rate", type="float", desc="持股比例"),
                      dict(name="season", type="int", desc="季度"),
                      dict(name="update_time", type="datetime", desc="更新时间"),
                      dict(name="year", type="int", desc="年份"),
                      ]),
        dict(table_name="etf_kline_day",
             table_comment="etf日k数据",
             indexes=dict(code_idx=[("code", 1)],
                          code_date_idx=[("date", -1), ("code", 1)]),
             columns=[
                 dict(name="code", type="str", desc="etf代码"),
                 dict(name="close", type="float", desc="收盘价"),
                 dict(name="date", type="datetime", desc="日期"),
                 dict(name="high", type="float", desc="最高点"),
                 dict(name="low", type="float", desc="最低点"),
                 dict(name="money", type="float", desc="成交额(万)"),
                 dict(name="open", type="float", desc="开盘价"),
                 dict(name="prev_close", type="float", desc="前一天收盘价"),
             ]),
        dict(table_name="calendar_event",
             table_comment="事件日历",
             columns=[
                 dict(name="id", type="str", desc="event有序id"),
                 dict(name="title", type="str", desc="收盘价"),
                 dict(name="start", type="datetime", desc="日期"),
             ]),

        dict(table_name="stock_share_change",
             table_comment="个股股本结构变更",
             indexes=dict(code_date_idx=[("code", 1), ("change_date", 1)]),
             columns=[
                 dict(name="change_reason", type="str", desc="变动原因"),
                 dict(name="change_date", type="datetime", desc="变动日期"),
                 dict(name="report_date", type="datetime", desc="公告日期"),
                 dict(name="total_capital_stock", type="float", desc="公告日期"),
                 dict(name="frozen_capital_stock", type="float", desc="流通受限股份"),
                 dict(name="flow_capital_stock", type="float", desc="已流通股份"),
                 dict(name="change_reason_code", type="float", desc="变动原因编码"),
             ]),
        dict(table_name="k_line_day_bfq",
             table_comment="个股日k线不复权",
             indexes=dict(date_code_idx=[("date", -1), ("code", 1)],
                          code_idx=[("code", 1)],
                          date_idx=[("date", -1)]),
             columns=[
                 dict(name="code", type="str", desc="代码"),
                 dict(name="close", type="float", desc="收盘价"),
                 dict(name="create_time", type="datetime", desc="创建时间"),
                 dict(name="date", type="datetime", desc="日期"),
                 dict(name="high", type="float", desc="最高点"),
                 dict(name="klt", type="str", desc="k线类型，101为日线"),
                 dict(name="low", type="float", desc="最低价"),
                 dict(name="money", type="float", desc="成交额"),
                 dict(name="open", type="float", desc="开盘价"),
                 dict(name="prev_close", type="float", desc="前一个交易日股价"),
                 dict(name="volume", type="float", desc="成交量"),
             ]),
        dict(table_name="trend_point",
             table_comment="个股趋势详情",
             indexes=dict(date_code_idx=[("date", -1), ("code", 1)],
                          code_idx=[("code", 1)]),
             columns=[
                 dict(name="date", type="datetime", desc="趋势变化时间点"),
                 dict(name="is_in_use", type="int", desc="当前是否在使用"),
                 dict(name="current_bot_trend_size", type="int", desc="底部趋势长度"),
                 dict(name="current_top_trend_size", type="int", desc="顶部趋势长度"),
                 dict(name="current_top_type_slope", type="int", desc="顶部趋势斜率"),
                 dict(name="current_bot_type_slope", type="int", desc="底部趋势斜率"),
                 dict(name="prev_top_type_slope", type="float", desc="上个拐点顶分型斜率"),
                 dict(name="prev_bot_type_slope", type="float", desc="上个拐点底分型斜率"),
                 dict(name="prev_trend_3", type="str", desc="趋势-3个点之前"),
                 dict(name="prev_trend_2", type="str", desc="趋势-2个点之前"),
                 dict(name="prev_trend_1", type="str", desc="趋势-1个点之前"),
                 dict(name="trend", type="str", desc="当前趋势"),
                 dict(name="trend_chain_start", type="datetime", desc="prev_trend_3点的开始时间"),
                 dict(name="inf_l_point_date", type="datetime", desc="底部反转发生时间"),
                 dict(name="inf_h_point_date", type="datetime", desc="顶部反转发生时间"),
                 dict(name="prev_inf_l_point_date", type="datetime", desc="上个底分型反转发生时间"),
                 dict(name="prev_inf_h_point_date", type="datetime", desc="上个顶峰型反转发生时间"),
                 dict(name="trend_change_scope", type="array", desc="顶底分型变化集合"),
                 dict(name="industry", type="str", desc="板块"),
                 dict(name="name", type="str", desc="个股名称"),
                 dict(name="code", type="str", desc="个股代号"),
                 dict(name="update", type="datetime", desc="更新时间，精确到天"),
                 dict(name="update_time", type="datetime", desc="更新时间，精确到秒"),
                 dict(name="inf_l_point_value", type="float", desc="顶部股价值"),
                 dict(name="inf_h_point_value", type="float", desc="底部股价值"),
                 dict(name="is_deleted", type="int", desc="是否被删除"),
                 dict(name="trend_type", type="int", desc="趋势类型")
             ]
             ),
        dict(table_name="k_line_day_comex_gold",
             table_comment="comex黄金日线",
             indexes=dict(code_date_idx=[("date", 1)]),
             columns=[
                 dict(name="date", type="datetime", desc="日期"),
                 dict(name="open", type="float", desc="开盘价"),
                 dict(name="high", type="float", desc="最高价"),
                 dict(name="low", type="float", desc="最低价"),
                 dict(name="close", type="float", desc="收盘价"),
                 dict(name="volume", type="float", desc="成交量"),
                 dict(name="position", type="float", desc="成交额"),
             ]),
    ]

    if table_name is not None:
        docs = [doc for doc in docs if doc['table_name'] in table_name]
        return docs

    return docs


def create_doc(table_name: list):
    # collist = db.list_collection_names()
    docs = list_doc(table_name)

    for doc in docs:
        table_name = doc['table_name']
        columns = doc['columns']
        indexes: dict = doc.get('indexes', {})
        table = db[table_name]
        record = table.find_one({}, sort=[('_id', -1)])
        if record is None:
            record = {column['name']: None for column in columns}
            table.insert_one(record)
            table.remove({})
        for index in indexes.values():
            table.create_index(index)


def run():
    db['rmb_fxrate'].insert_one({'date': None, 'us': None, 'eur': None, 'jp': None})

    # 自定义板块,需要定时同步
    db.custom_board_detail.create_index([("board", 1)])
    # 个股训练分析表
    db.stock_training_picker.create_index([("start_scope", -1), ("code", 1)])
    # 股东分析
    db.stock_gdfx.create_index([("code", 1)])
    db.stock_gdfx.create_index([("date", -1), ("code", 1)])

    # 板块成交量
    db.board_trade_volume.create_index([("date", -1), ("industry", 1)])

    db.trend_data.create_index([("date", -1), ("industry", 1)])
    db.trend_point.create_index([("code", 1)])
    db.trend_point.create_index([("date", -1), ("code", 1)])

    db.etf_feature.create_index([("code", 1)])
    db.etf_feature.create_index([("date", -1), ("code", 1)])

    db.etf_kline_day.create_index([("code", 1)])
    db.etf_kline_day.create_index([("date", -1), ("code", 1)])
    docs = ["k_line_day", "board_k_line_day", "stock_feature", "stock_detail", "stock_value", "report_data"]
    for doc in docs:
        create_doc(doc)
    db.k_line_month.create_index([("date", 1), ("code", 1)])
    db.board_k_line_day.create_index([("name", 1), ("date", 1)])
    db.board_k_line_day.create_index([("name", 1)])
    db.k_line_day.create_index([("code", 1)])
    db.k_line_day.create_index([("date", 1), ("code", 1)])
    db.k_line_day.create_index([("date", 1)])
    db.special_stock.create_index([("date", 1)])

    db.stock_feature.create_index([("code", 1)])
    db.stock_feature.create_index([("date", 1), ("code", 1)])
    db.stock_detail.create_index([("code", 1)])
    db.stock_value.create_index([("date", 1), ("code", 1)])
    db.market_status.create_index([("date", 1)])

    db.rps_anslysis.create_index([("code", 1), ("date", 1)])


def add_config_data():
    db['config'].insert_one(dict(
        name="board",
        value=['猪肉概念', "白酒", "氢能源", "沪市", "深市", "科创板", "创业板"]
    ))

    db['my_work'].insert_one({
        "name": "definition",
        "current": "锦浪科技",
        "latest": "海马汽车",
        "edited_stock_size": 180,
        "tag_size": 263
    })

    db["ind_query_store"].insert_one({
        "body": "{\n    \"params\": [\n        {\n            \"name\": \"current_bot_type_slope\",\n            \"value\": [\n                \"$gt\",\n                0\n            ]\n        },\n        {\n            \"name\": \"inf_l_point_date\",\n            \"value\": [\n                \"$gte\",\n                \"#get_work_date($date,12)\"\n            ]\n        },\n        {\n            \"name\": \"current_max_high_type\",\n            \"value\": [\n                \"$gte\",\n                {\n                    \"$multiply\": [\n                        \"$features.close\",\n                        0.9\n                    ]\n                }\n            ]\n        },\n        {\n            \"name\": \"current_max_high_type\",\n            \"value\": [\n                \"$lte\",\n                {\n                    \"$multiply\": [\n                        \"$features.close\",\n                        1.1\n                    ]\n                }\n            ]\n        },\n        {\n            \"name\": \"inf_l_point_value\",\n            \"value\": [\n                \"$lte\",\n                {\n                    \"$multiply\": [\n                        \"$features.close\",\n                        1.05\n                    ]\n                }\n            ]\n        },\n        {\n            \"name\": \"rate\",\n            \"value\": [\n                \"$gt\",\n                1\n            ]\n        },\n        {\n            \"name\": \"money_median\",\n            \"value\": [\n                \"$gt\",\n                60000000\n            ]\n        },\n        {\n            \"name\": \"current_bot_trend_size\",\n            \"value\": [\n                \"$gte\",\n                3\n            ]\n        }\n    ],\n    \"date\": \"#current_date\",\n    \"until\": \"#current_date\",\n    \"custom\": {\n        \"onlyCode\": false,\n        \"aimBoard\": \"\"\n    }\n}",
        "name": "趋势反转",
        "desc": "通过某些特征获取趋势反转的个股,再根据板块效应进行推荐",
        "msg_template": "",
        "key": "trend_reversal",
        "in_use": 1
    })


if __name__ == "__main__":
    create_doc(['k_line_day_comex_gold'])
    # add_config_data()
