from app.main.stock.job import board_association, sync_indicator
from app.main.task import trend_task, stock_task, \
    indicator_task, board_task, history_task, fund_task, macrodata_task

TASK_SYNC_STOCK_IND = "SYNC_STOCK_IND"
TASK_TYPE_CELERY = 'TASK_CELERY'
TASK_TYPE_TASK_FLOW = 'TASK_FLOW'
TASK_TYPE_HISTORY_TASK = 'HISTORY_TASK'

# 同步个股日k线
# 个股特征跑批-个股趋势跑批-板块趋势和成交额聚合-

TASK_MAPPING = {
    "更新个股的板块信息": board_task.sync_board_stock_detail,
    "个股趋势跑批": trend_task.submit_trend_task,
    "清空个股趋势数据":trend_task.clear_trend_point,
    "个股特征跑批": stock_task.submit_stock_feature_by_job,
    '板块趋势和成交额聚合': trend_task.trend_data_task,
    '同步个股历史市值': fund_task.stock_value_backtrading, # 异步无回调任务

    "个股历史特征按批次跑批": history_task.submit_history_stock_feature_by_job,  # 名字不能随便改,改之前全局搜一下
    "个股历史趋势按批次跑批": history_task.submit_history_stock_trend_by_job,
    '板块趋势和成交额按批次聚合': history_task.submit_agg_stock_trend_by_job,
    '同步个股股本结构变更记录': stock_task.sync_stock_share_change,  # 异步无回调任务,该任务要控制频率，太快会被ban ip

    '清空日k数据': stock_task.clear_k_line_by_job,
    '同步个股日k线': stock_task.sync_stock_k_line_by_job,
    '同步个股日k线不复权': stock_task.sync_stock_k_line_bfq_by_job,
    '同步个股月k线': stock_task.submit_stock_month_task,
    '同步东财板块日k线': board_task.sync_board_k_line,
    '保存趋势信息': trend_task.dump_trend_info,  # 异步无回调任务
    "同步人民币对外币汇率": indicator_task.sync_cny_fx,  # 同步任务
    "同步pmi": sync_indicator.sync_pmi,  # 同步pmi
    '查询趋势信息': trend_task.query_trend_info,  # 同步任务
    '个股关联板块': board_association.associate,  # 同步任务
    '扫描个股特征任务': history_task.start_stock_feature_task,
    '同步etf基金历史k线': fund_task.sync_etf_kline,  # 异步无回调任务
    '同步etf基金盘中k线': fund_task.sync_etf_kline_real_time,  # 异步无回调任务
    "同步comex黄金期货": indicator_task.sync_comex_gold,  # 异步无回调任务
    '美联储利率决议报告': indicator_task.sync_fed_interest_rate,  # 异步无回调任务

    '股市资金抱团分析': macrodata_task.baotuan_update
}

# 需要回调的任务
PATH_TASK_MAPPING = {
    "app.main.task.stock_task.sync_stock_data": "同步个股日k线",
    "app.main.task.trend_task.sync_trend_task": "个股趋势跑批",
    "app.main.task.stock_task.sync_stock_feature": "个股特征跑批",
    "app.main.task.trend_task.trend_data_task": "板块趋势和成交额聚合",
    "app.main.task.board_task.sync_data": "同步东财板块日k线",
    "app.main.task.stock_task.sync_stock_month_data": "同步个股月k线"
}

ASYNC_NO_CALLBACK = ['同步etf基金历史k线', '同步etf基金盘中k线', '保存趋势信息', '股市资金抱团分析',
                     '同步comex黄金期货', '美联储利率决议报告', '同步个股股本结构变更记录','同步个股历史市值']
