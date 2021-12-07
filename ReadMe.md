
## 定时任务

```
celery -A manage.celery beat -l info
```

## flower

```
 celery --broker='redis://:ironBackRedis123@172.16.1.184:30004/1' flower
```

##

```
 celery -A manage.celery worker -l info -P  eventlet -c 500 -n worker4.%h
```