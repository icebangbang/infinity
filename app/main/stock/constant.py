boll_top_slope = "boll_top_slope"

current_top_type_slope = "current_top_type_slope"
prev_top_type_slope = "prev_top_type_slope"

current_bot_type_slope = "current_bot_type_slope"
prev_bot_type_slope = "prev_bot_type_slope"

inf_h_point_date = "inf_h_point_date"
inf_l_point_date = "inf_l_point_date"

inf_h_point_value = "inf_h_point_value"
inf_l_point_value = "inf_l_point_value"
current_max_high_type = "current_max_high_type"

current_top_trend_size = "current_top_trend_size"
prev_top_trend_size = "prev_top_trend_size"

current_bot_trend_size = "current_bot_trend_size"
prev_bot_trend_size = "prev_bot_trend_size"

box_boundary = "box_boundary"
ma5 = "ma5"
ma10 = "ma10"
ma20 = "ma20"
ma30 = "ma30"
ma60 = "ma60"
ma200 = "ma200"
ma250 = "ma250"
vol_avg_10 = "vol_avg_10"
vol_avg_5 = "vol_avg_5"
volume = "volume"
close = "close"
high = "high"
rate = "rate"
gap = "gap"
up_shadow = "up_shadow"
down_shadow = "down_shadow"
entity_length = "entity_length"
close_rate_5 = "close_rate_5"
close_rate_10 = "close_rate_10"

ma5_upon_20 = "ma5_upon_20"
ma10_upon_20 = "ma10_upon_20"
ma5_upon_10 = "ma5_upon_10"
ma10_upon_10 = "ma10_upon_10"
ma5_upon_5 = "ma5_upon_5"
ma10_upon_5 = "ma10_upon_5"
ma5_upon_max = "ma5_upon_max"
ma10_upon_max = "ma10_upon_max"

# W&R
# 威廉指标
wr_6 = "wr_6"
wr_10 = "wr_10"

# 涨跌中位数
up_median = "up_median"
down_median = "down_median"

increase_avg_rate_5 = "increase_avg_rate_5"
increase_avg_rate_10 = "increase_avg_rate_10"
increase_avg_rate_20 = "increase_avg_rate_20"

earning_rate_1 = "earning_rate_1"
earning_rate_2 = "earning_rate_2"
earning_rate_3 = "earning_rate_3"
earning_rate_5 = "earning_rate_5"
earning_rate_10 = "earning_rate_10"
earning_rate_15 = "earning_rate_15"
earning_rate_20 = "earning_rate_20"

feature = {
    "current_max_high_type": "当前趋势顶分型最大值",
    "current_top_type_slope": "当前趋势顶分型斜率",
    "current_bot_type_slope": "当前趋势底分型斜率",
    "prev_top_type_slope": "先前趋势顶分型斜率",
    "prev_bot_type_slope": "先前趋势底分型斜率",
    "inf_h_point_date": "顶分型趋势拐点时间",
    "inf_l_point_date": "底分型趋势拐点时间",
    "box_boundary": "箱体周期",
    "ma5": "5日均线",
    "ma10": "10日均线",
    "ma20": "20日均线",
    "ma30": "30日均线",
    "ma60": "60日均线",
    "ma200": "200日均线",
    "ma250": "250日均线",
    "vol_avg_10": "10日均量",
    "volume": "当前成交量",
    "close": "当前价格",
    "high": "当日最高价",
    "rate": "当前涨幅",
    "gap": "缺口",
    "up_shadow": "上影线长度",
    "entity_length": "实体长度",
    "down_shadow": "下影线长度",
    "increase_avg_rate_5": "近5日日均涨幅",
    "increase_avg_rate_10": "近10日日均涨幅",
    "increase_avg_rate_20": "近20日日均涨幅",
    "close_rate_5": "5日内涨幅",
    "close_rate_10": "10日内涨幅",
    "ma5_upon_max": "最大连续在5日线之上次数",
    "ma10_upon_max": "最大连续在10日线之上次数",
    "boll_top_slope": "布林轨道上沿斜率"
}

feature_detail = [
dict(
        name="current_max_high_type",
        desc="当前趋势顶分型最大值",
        type="float",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=None,
        category="趋势"
    ),
    dict(
        name="inf_h_point_value",
        desc="顶分型趋势拐点值",
        type="float",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=None,
        category="趋势"
    ),
    dict(
        name="inf_l_point_value",
        desc="底分型趋势拐点值",
        type="float",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=None,
        category="趋势"
    ),
    dict(
        name="inf_h_point_date",
        desc="顶分型趋势拐点时间",
        type="date",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=None,
        category="趋势"
    ),
    dict(
        name="inf_l_point_date",
        desc="底分型趋势拐点时间",
        type="date",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=None,
        category="趋势"
    ),

    dict(
        name="current_bot_trend_size",
        desc="当前底分型趋势的交易日数",
        type="float",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="趋势"
    ),
    dict(
        name="current_top_type_slope",
        desc="当前趋势顶分型斜率",
        type="float",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="趋势"
    ),
    dict(
        name="current_bot_type_slope",
        desc="当前趋势底分型斜率",
        type="float",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="趋势"
    ),
    dict(
        name="prev_top_type_slope",
        desc="先前趋势顶分型斜率",
        type="float",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="趋势"
    ),
    dict(
        name="prev_bot_type_slope",
        desc="先前趋势底分型斜率",
        type="float",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="趋势"
    ),
    dict(
        name="ma5_upon_5",
        desc="5日内站上5日均线次数",
        type="int",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="均线"
    ),
    dict(
        name="ma5_upon_10",
        desc="10日内站上5日均线次数",
        type="int",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="均线"
    ),
    dict(
        name="ma5_upon_20",
        desc="20日内站上5日均线次数",
        type="int",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="均线"
    ),
    dict(
        name="ma10_upon_5",
        desc="5日内站上10日均线次数",
        type="int",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="均线"
    ),
    dict(
        name="ma10_upon_10",
        desc="10日内站上10日均线次数",
        type="int",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="均线"
    ),
    dict(
        name="ma10_upon_20",
        desc="20日内站上10日均线次数",
        type="int",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="均线"
    ),
    dict(
        name="ma5_upon_max",
        desc="最大连续在5日线之上次数",
        type="int",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="均线"
    ),
    dict(
        name="ma10_upon_max",
        desc="最大连续在10日线之上次数",
        type="int",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="均线"
    ),
    dict(
        name="volume_gt_5",
        desc="最大连续在10日线之上次数",
        type="int",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="均线"
    ),
dict(
        name="rate",
        desc="涨幅",
        type="float",
        filter_style=1,
        comparator=["eq", "lte", "gte"],
        default_comparator="gte",
        default_value=0,
        category="基础"
    )

]


def get_feature_keys():
    return [f['name'] for f in feature_detail]
