# from celery import Celery
#
# celery = Celery(
#     "sdds",
#     backend="redis://:ironBackRedis123@172.16.1.184:30004/1",
#     broker="redis://:ironBackRedis123@172.16.1.184:30004/1"
# )
# inspect = celery.control.inspect()
# stats = inspect.stats()
# # 查看当前运行的任务
# active = inspect.active()
# # 查看当前接收但未执行的任务
# reserved = inspect.reserved()
# # 查看queues
# queue = inspect.active_queues()
#
# print(123)