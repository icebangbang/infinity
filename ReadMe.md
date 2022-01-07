
## 定时任务

```
celery -A manage.celery beat -l info
```

## flower

```
 celery --broker='redis://:ironBackRedis123@39.105.104.215:30004/1' flower
```

##

```
 celery -A manage.celery worker -l info -P  eventlet -Q day_level -c 500 -n worker4.%h
 celery -A manage.celery worker -l info -P  eventlet -Q indicator -c 500 -n worker5.%h
```