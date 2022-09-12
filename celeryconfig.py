from kombu import Exchange, Queue
from celery.schedules import crontab

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
    {'app.main.task.stock_task.sync_stock_month_data': {
        'queue': 'day_level',
        'routing_key': 'day_level'
    }
    },

    {'app.main.task.stock_task.submit_stock_month_task': {
        'queue': 'day_level',
        'routing_key': 'day_level'
    }
    },
    {'app.main.task.stock_task.submit_stock_feature': {
        'queue': 'default',
        'routing_key': 'default'
    }
    },
    {'app.main.task.etf_task.submit_etf_feature': {
        'queue': 'default',
        'routing_key': 'default'
    }
    },
    {'app.main.task.trend_task.submit_trend_task': {
        'queue': 'default',
        'routing_key': 'default'
    }
    },
    {'app.main.task.trend_task.get_trend_data_task': {
        'queue': 'day_level',
        'routing_key': 'day_level'
    }
    },
    {'app.main.task.stock_task.submit_stock_ind_task': {
        'queue': 'default',
        'routing_key': 'default'
    }
    },
    {'app.main.task.stock_task.sync_stock_feature': {
        'queue': 'indicator',
        'routing_key': 'indicator'
    }
    },
    {'app.main.task.stock_task.sync_stock_ind': {
        'queue': 'indicator',
        'routing_key': 'indicator'
    }
    },
    {'app.main.task.etf_task.sync_etf_feature': {
        'queue': 'indicator',
        'routing_key': 'indicator'
    }
    },
    {'app.main.task.trend_task.sync_trend_task': {
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
    {'app.main.task.fund_task.backtrading': {
        'queue': 'day_level',
        'routing_key': 'day_level'
    }
    },
    {'app.main.task.stock_task.sync_balance': {
        'queue': 'day_level',
        'routing_key': 'day_level'
    }
    },
    {'app.main.task.stock_task.sync_cash_flow': {
        'queue': 'day_level',
        'routing_key': 'day_level'
    }
    },
    {'app.main.task.stock_task.sync_profit': {
        'queue': 'day_level',
        'routing_key': 'day_level'
    }
    },
    {'app.main.task.stock_task.sync_analysis_indicator': {
        'queue': 'day_level',
        'routing_key': 'day_level'
    }
    },
    # 提交特征任务,做任务拆分
    {'app.main.task.board_task.submit_board_feature': {
        'queue': 'default',
        'routing_key': 'default'
    }
    },
    # 拆分任务具体执行者
    {'app.main.task.board_task.sync_board_feature': {
        'queue': 'indicator',
        'routing_key': 'indicator'
    }
    },
    {'app.main.task.house_task.sync_hangzhou_house': {
        'queue': 'default',
        'routing_key': 'default'
    }
    },
)

beat_schedule = {
    'stock_data_sync':
        {  # 股票数据同步
            "task": "app.main.task.stock_task.sync_stock_k_line",  # 任务函数所在位置
            "schedule": 180,  # 定时每300秒执行一次
        },
    'sync_index_data':
        {  # 股票数据同步
            "task": "app.main.task.stock_task.sync_index_data",  # 任务函数所在位置
            "schedule": 30,  # 定时每300秒执行一次
        },
    'stock_month_data_sync':
        {  # 股票月线数据同步
            "task": "app.main.task.stock_task.submit_stock_month_task",  # 任务函数所在位置
            "schedule": 600,  # 定时每10分钟执行一次
        },
    'board_data_sync': {
        "task": "app.main.task.board_task.sync_board_k_line",
        "schedule": 60,  # 定时每120秒执行一次
    },
    'sync_board_stock_detail': {
        "task": "app.main.task.board_task.sync_board_stock_detail",
        "schedule": crontab(minute='1', hour='15', day_of_week='1-5')  # 工作日的15点以后
    },
    'sync_board_stock_ind': {
        "task": "app.main.task.stock_task.submit_stock_ind_task",
        "schedule": 6000  # 每20分钟执行一次
    },
    'get_stock_feature': {
        "task": "app.main.task.stock_task.submit_stock_feature",
        "schedule": 300  # 每5分钟执行一次
    },
    'get_trend_point': {  # 趋势数据收集
        "task": "app.main.task.trend_task.submit_trend_task",
        "schedule": 600000000  # 每10分钟执行一次
    },
    'get_trend_data': {  # 趋势数据聚合
        "task": "app.main.task.trend_task.get_trend_data_task",
        "schedule": 120000000
    },
    'sync_macrodata': {
        "task": "app.main.task.macrodata_task.sync",
        "schedule": 400
    },
    'sync_baotuan': {
        "task": "app.main.task.macrodata_task.baotuan_update",
        "schedule": crontab(minute='1', hour='16', day_of_week='1-5')
    },
    'market_status_analysis': {
        "task": "app.main.task.macrodata_task.market_status_analysis",
        "schedule": 5
    },
    'sync_hangzhou_house': {
        "task": "app.main.task.house_task.sync_hangzhou_house",
        "schedule": 30
    },
    'sync_fund_flow': {
        "task": "app.main.task.fund_task.backtrading",
        "schedule": 1800
    },
    'send_remind_msg': {
        "task": "app.main.task.remind_task.stock_remind",
        "schedule": 20
    },
    'rps_analysis_250': {  # 250日30日rps统计
        "task": "app.main.task.stock_task.sync_rps_analysis_250",
        "schedule": 1200
    }, 'rps_analysis_120': {  # 120日30日rps统计
        "task": "app.main.task.stock_task.sync_rps_analysis_120",
        "schedule": 1000
    }, 'rps_analysis_60': {  # 60日rps统计
        "task": "app.main.task.stock_task.sync_rps_analysis_60",
        "schedule": 800
    }, 'rps_analysis_30': {  # 30日rps统计
        "task": "app.main.task.stock_task.sync_rps_analysis_30",
        "schedule": 600
    }, 'sync_bellwether': {  # 同步领头羊
        "task": "app.main.task.stock_task.sync_bellwether",
        "schedule": 30
    }

}

# 在出现worker接受到的message出现没有注册的错误时，使用下面一句能解决
imports = ("app.main.task.macrodata_task",
           "app.main.task.house_task",
           "app.main.task.fund_task",
           "app.main.task.remind_task")
