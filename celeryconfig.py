from celery.schedules import crontab
from kombu import Exchange, Queue

# 配置时区
timezone = 'Asia/Shanghai'

# broker_url = 'redis://:ironBackRedis123@39.105.104.215:30004/1'
# RESULT_BACKEND = 'redis://:ironBackRedis123@39.105.104.215:30004/1'
# 定义一个默认交换机
default_exchange = Exchange('default', type='direct')

# 定义一个指标专用交换机
indicator_exchange = Exchange('indicator', type='direct')
day_level_exchange = Exchange('day_level', type='direct')

# 创建三个队列，一个是默认队列，一个是video、一个image
task_queues = (
    Queue('default', default_exchange, routing_key='default'),
    Queue('indicator', indicator_exchange, routing_key='indicator'),
    Queue('day_level', day_level_exchange, routing_key='day_level'),
)

task_default_queue = 'default'
task_default_exchange = 'default'
task_default_routing_key = 'default'
#
task_routes = (
    {'app.main.task.stock_task.sync_stock_k_line': {
        'queue': 'day_level',
        'routing_key': 'day_level'
    }
    },

    {'app.main.task.stock_task.transform_task': {
        'queue': 'day_level',
        'routing_key': 'day_level'
    }
    },

    {'app.main.task.stock_task.sync_stock_data': {
        'queue': 'day_level',
        'routing_key': 'day_level'
    }
    },

    {'app.main.task.stock_task.submit_stock_feature': {
        'queue': 'default',
        'routing_key': 'default'
    }
    },
    {'app.main.task.stock_task.sync_stock_feature': {
        'queue': 'indicator',
        'routing_key': 'indicator'
    }
    },
    {'app.main.task.board_task.sync_board_k_line': {
        'queue': 'day_level',
        'routing_key': 'day_level'
    }
    },
    {'app.main.task.board_task.sync_data': {
        'queue': 'day_level',
        'routing_key': 'day_level'
    }
    },
    {'app.main.task.board_task.submit_board_feature': {
        'queue': 'default',
        'routing_key': 'default'
    }
    },
    {'app.main.task.board_task.sync_board_feature': {
        'queue': 'indicator',
        'routing_key': 'indicator'
        }
    },
)


beat_schedule = {
    'stock_data_sync': {  # 股票数据同步
        "task": "app.main.task.stock_task.sync_stock_k_line",  # 任务函数所在位置
        "schedule": 100,  # 定时每300秒执行一次
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
        "schedule": 400  # 每5分钟执行一次
    },
    'get_board_feature': {
        "task": "app.main.task.board_task.submit_board_feature",
        "schedule": 400
    }
}

# 在出现worker接受到的message出现没有注册的错误时，使用下面一句能解决
# CELERY_IMPORTS = ("app.main.task.stock_task",)
