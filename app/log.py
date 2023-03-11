import logging
import logging.config
import os


def init_log(app):
    logging.getLogger("nacos.client").setLevel(logging.WARNING)
    # env = app.config['FLASK_ENV']
    env = os.environ.get('FLASK_ENV')
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
