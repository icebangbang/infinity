from app.main.task import trend_task

TASK_SYNC_STOCK_IND = "SYNC_STOCK_IND"

TASK_TYPE_CELERY = 'TASK_CELERY'
TASK_TYPE_TASK_FLOW = 'TASK_FLOW'

TASK_MAPPING = {
    "个股趋势跑批": trend_task.submit_trend_task,
    "个股特征跑批": trend_task.submit_trend_task,
    '板块趋势聚合':trend_task.submit_trend_task,
    '板块成交额聚合':trend_task.submit_trend_task
}
