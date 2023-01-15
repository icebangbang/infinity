from app.main.task import trend_task, stock_task, fx_task

TASK_SYNC_STOCK_IND = "SYNC_STOCK_IND"

TASK_TYPE_CELERY = 'TASK_CELERY'
TASK_TYPE_TASK_FLOW = 'TASK_FLOW'

TASK_MAPPING = {
    "个股趋势跑批": trend_task.submit_trend_task,
    "个股特征跑批": stock_task.submit_stock_feature_by_job,
    '板块趋势和成交额聚合': trend_task.get_trend_data_task,
    '同步个股日k线': stock_task.sync_stock_k_line_by_job,
    "同步人民币对外币汇率": fx_task.sync_cny_fx # 同步任务
}
