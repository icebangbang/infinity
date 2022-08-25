
## 定时任务

## 个股趋势相关
先分析个股的趋势走向`app.main.task.trend_task.submit_trend_task`
然后通过个股的趋势走向,归并板块的趋势走势`get_trend_data_task`





## flower

```
 celery --broker='redis://:ironBackRedis123@39.105.104.215:30004/1' flower
```

## 

```
 celery -A manage.celery worker -l info -P  eventlet -Q day_level -c 500 -n worker4.%h
 celery -A manage.celery worker -l info -P  eventlet -Q indicator -c 500 -n worker5.%h
```