from app import application
import os
from celery.schedules import crontab

# 获取环境变量,
# pycharm启动可以在 RUN/DEBUG Configuration-Environment variables中添加FLASK_ENV
# 线上启动在 honeybee.sysconfig中指定
env = os.environ.get('FLASK_ENV') or 'development'
app = application.create_app(env)  # from .main.rest import rest as main_blueprint

from app.celery_worker import celery

celery.conf.beat_schedule = {
    'stock_data_sync': {  # 股票数据同步
        "task": "app.main.task.stock_task.sync_stock_k_line",  # 任务函数所在位置
        "schedule": 300,  # 定时每300秒执行一次
    },
    'board_data_sync': {
        "task": "app.main.task.board_task.sync_board_k_line",
        "schedule": 420,  # 定时每420秒执行一次
    },
    'sync_board_stock_detail': {
        "task": "app.main.task.board_task.sync_board_stock_detail",
        "schedule": crontab(minute='1', hour='15', day_of_week='1-5')  # 工作日的15点以后
    },
    'get_stock_feature': {
        "task": "app.main.task.stock_task.submit_stock_feature",
        "schedule": 300  # 每5分钟执行一次
    }
}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8191, debug=True, use_reloader=False, threaded=True)
