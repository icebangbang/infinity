from app.main.db.mongo import db


def create_doc(doc_name):
    collist = db.list_collection_names()
    if doc_name not in collist:
        data_set = db[doc_name]
        data_set.insert_one({})
        data_set.remove({})


def run():
    db['rmb_fxrate'].insert_one({'date':None, 'us':None, 'eur':None, 'jp':None})

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
    run()
    # add_config_data()
