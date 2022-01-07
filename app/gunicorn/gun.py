# coding=utf-8
from gevent import monkey;monkey.patch_all()

debug = False
loglevel = 'info'
# bind = '0.0.0.0:8191'
pidfile = '/var/log/dao/project.pid'
accesslog = '/var/log/dao/access.log'
errorlog = '/var/log/dao/project.log'
# access_log_format = '%(h)s %(l)s %(u)s %(t)s'

# 启动的进程数
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 5
timeout = 300
worker_class = 'gunicorn.workers.ggevent.GeventWorker'
x_forwarded_for_header = 'X-FORWARDED-FOR'
# chdir = '/opt/honeybee-pkg/'
chdir = '/'

# log_config ='/Users/lifeng/Work/Code/honeybee-new/app/conf/gunicorn_logging.conf'
