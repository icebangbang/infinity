import logging

from app.main.stock.dao import board_dao
from app.main.utils import restful
from . import rest
from app.main.task import demo
from app.main.task import board_task
from app.celery_worker import celery
from app.main.task import board_task


@rest.route("/celery/board", methods=['get'])
def maunlly():
    boards = board_dao.get_all_board()
    # 获取最近一个交易日

    step = int(len(boards) / 100)
    boards_group = [boards[i:i + step] for i in range(0, len(boards), step)]
    for index, boards in enumerate(boards_group):
        logging.info("提交同步任务,时序{}".format(index))
        board_task.sync_data.apply_async(args=[boards])

    return restful.response("ok")
