if __name__ == "__main__":
    from app.main.db.mongo import db
    import json

    ind_query_store = db['ind_query_store']

    new_store = {}
    new_store['body'] = json.dumps({
        "params": [
            {"name": "current_bot_type_slope", "value": ["$gt", 0]},
            {"name": "inf_l_point_date", "value": ["$gte", "#get_work_date($date,12)"]},
            {"name": "current_max_high_type", "value": ["$gte", {"$multiply": ["$features.close", 0.9]}]},
            {"name": "current_max_high_type", "value": ["$lte", {"$multiply": ["$features.close", 1.10]}]},
            {"name": "inf_l_point_value", "value": ["$lte", {"$multiply": ["$features.close", 1.05]}]},
            {"name": "rate", "value": ["$gt", 1]},
            {"name": "current_bot_trend_size", "value": ["$gte", 3]}
        ],
        "date": "#current_date",
        "until": "#current_date",
        "custom": {
            "onlyCode": False,
            "aimBoard": ""
        }
    },indent=4)

    new_store['name'] = "趋势反转"
    new_store['desc'] = "通过某些特征获取趋势反转的个股,再根据板块效应进行推荐"
    new_store['msg_template'] = ""
    new_store['key'] = "trend_reversal"
    new_store['in_use'] = 1

    ind_query_store.update_one({"key": "trend_reversal"}, {"$set": new_store}, upsert=True)
