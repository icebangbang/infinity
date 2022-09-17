
## 定时任务

## 个股趋势相关
### /celery/stock/trend
1. 先分析个股的趋势走向.
`app.main.task.trend_task.submit_trend_task`
2. 然后通过个股的趋势走向,归并板块的趋势走势.`get_trend_data_task`

## 整体板块趋势相关





## flower

```
 celery --broker='redis://:ironBackRedis123@39.105.104.215:30004/1' flower
```

## 其他脚本

查看所有用户代码提交行数
```shell script
git log --format='%aN' | sort -u | while read name; do echo -en "$name\t"; git log --author="$name" --pretty=tformat: --numstat | awk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "added lines: %s, removed lines: %s, total lines: %s\n", add, subs, loc }' -; done
```

查看用户代码提交次数
```shell script
git shortlog -s -n
```

```
 celery -A manage.celery worker -l info -P  eventlet -Q day_level -c 500 -n worker4.%h
 celery -A manage.celery worker -l info -P  eventlet -Q indicator -c 500 -n worker5.%h
```