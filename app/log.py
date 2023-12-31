import logging
import logging.config
import os


def get_logger(name):
    return logging.getLogger(name)


def init_log(app=None):
    logging.getLogger("nacos.client").setLevel(logging.WARNING)
    logging.getLogger("urllib3.util.retry").setLevel(logging.INFO)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)
    # env = app.config['FLASK_ENV']
    env = os.environ.get('FLASK_ENV','local')
    if "local" not in env.lower():
        return

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                'format': '%(asctime)s [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
            },
            'standard': {
                'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            }
        },

        # "loggers": {
        #     "app_name": {
        #         "level": "INFO",
        #         "handlers": ["console"],
        #         "propagate": "no"
        #     }
        # },

        "root": {
            'handlers': ['console'],
            'level': "DEBUG",
            'propagate': False
        }
    }
    logging.config.dictConfig(LOGGING)


init_log()
