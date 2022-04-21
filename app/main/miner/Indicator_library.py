trend_reversal = {
    "params": {
        "current_bot_type_slope": ["$gt", 0],
        "inf_l_point_date": ["$gte", "#get_work_date($date,10)"],
        "current_max_high_type": ["$lte", "$features.close"]
    },
    "name": "趋势反转",
    "key": "trend_reversal",
    "msg_template": "提醒:{stock_code}[{name}]在出现底部反转{inf_l_point_value}[{inf_l_point_date}],当前价格突破前期小高位{current_max_high_type},"
}

trend_reversal_trading = {
    "params": [
        {"name": "current_bot_type_slope", "value": ["$gt", 0]},
        {"name": "inf_l_point_date", "value": ["$gte", "#get_work_date($date,10)"]},
        {"name": "current_max_high_type", "value": ["$gte", {"$multiply": ["$features.close", 1.02]}]},
        {"name": "current_max_high_type", "value": ["$lte", {"$multiply": ["$features.close", 1.07]}]},
        {"name": "inf_l_point_value", "value": ["$lte", {"$multiply": ["$features.close", 1.05]}]},
        {"name": "rate", "value": ["$gte", 2.0]},
        {"name": "current_bot_trend_size", "value": ["$gte", 3]}
    ],
    "name": "趋势反转",
}
