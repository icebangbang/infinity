import logging

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已存在的日志器
    'formatters': {
        # 日志信息显示格式
        'simple': {
            'format': '%(asctime)s \"%(module)s:%(funcName)s:%(lineno)d\" [%(levelname)s - %(message)s]',
        },
    },
    'handlers': {
        'celery': {
            # 向文件中输出日志
            'level': 'INFO',
            'class': 'concurrent_log_handler.ConcurrentRotatingFileHandler',
            'maxBytes': 5 * 1024 * 1024,  # 分割大小（5M）
            'backupCount': 10,  # 保存10份
            'filename': 'log.log',  # 日志文件位置
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        # 日志器
        'celery_log': {
            'handlers': ['celery'],
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO'  # 日志器接收的最低日志级别
        }
    },
}

# logging.config.dictConfig(LOG_CONFIG)
