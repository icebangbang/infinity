## 项目诞生于
2021-08-30 14:31
辛丑年 丙申月 庚戌日 癸未时

## 定时任务

## 数据初始化相关
### 配置个股详情
同步board_detail，stock_detail
相关方法：`app.main.stock.job.sync_board.sync`

### 个股关联板块
stock_detail添加industry
`app.main.stock.job.board_association.associate`

### 报团分析
首页抱团分析数据展示
`app.main.stock.service.report_service.baotuan_analysis`

### 个股特征筛选
`app.main.stock.service.stock_service.stock_remind_v2`

### 个股特征跑批
`app.main.rest.celery.get_stock_feature`

### 清数据重跑 
`app.main.local.temp.clear_stock_info`


## 个股趋势相关
### /celery/stock/trend
1. 先分析个股的趋势走向.
`app.main.task.trend_task.submit_trend_task`
2. 然后通过个股的趋势走向,归并板块的趋势走势.
`app.main.task.trend_task.get_trend_data_task`

## 整体板块趋势相关


## 财报

1. stock_profit 利润表
2. stock_cash_flow 现金流
3. 资产负债表数据同步
`app.main.stock.job.sync_performance.sync_balance`


## flower

```
 celery -A manage.celery --broker='redis://:ironBackRedis123@localhost:30004/1' flower
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