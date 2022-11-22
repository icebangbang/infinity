from app.main.db.mongo import db
from app.main.stock.job import job_config
from app.main.utils import simple_util, date_util
from datetime import datetime

def test():
    method = simple_util.get_method_by_path("app.main.task.stock_task.auto_submit_stock_feature")
    method.apply_async(kwargs=dict())


def clear_stock_info():
    """
    清空个股k线
    :return:
    """

    db['k_line_day'].drop()
    # db['k_line_month'].drop()
    # db.k_line_month.create_index([("date", 1), ("code", 1)])
    db.k_line_day.create_index([("code", 1)])
    db.k_line_day.create_index([("date", 1), ("code", 1)])
    db.k_line_day.create_index([("date", 1)])

    db['stock_feature'].drop()
    db.stock_feature.create_index([("code", 1)])
    db.stock_feature.create_index([("date", 1), ("code", 1)])

    job_config.acquire_job("app.main.task.stock_task.sync_stock_k_line")

    method = simple_util.get_method_by_path("app.main.task.stock_task.sync_stock_k_line")
    method.apply_async(kwargs=dict(rebuild_data=1))


def trend_data_task():
    method = simple_util.get_method_by_path("app.main.task.trend_task.get_trend_data_task")
    kwargs = {
        "from_date_ts": 1648742400000,
        "end_date_ts": 1660924800000,
        "global_task_id": "1fd1716e-1fda-11ed-934b-00163e0a10b2"
    }
    method.apply_async(kwargs= kwargs)

def rps_test():
    board_detail = db['board_detail']
    rps_anslysis = db['rps_anslysis']
    trend_point = db['trend_point']
    another_boards = list(board_detail.find({"board": {"$in": ['游戏']}}))
    for another_board in another_boards:
        total = another_board['codes']
        r = list(rps_anslysis.find(
            {"code": {"$in": total},
             "date": datetime(2022,9,13),
             "span":30}).sort("rate",-1))
        pass
def trend_detail():
    board_detail = db['board_detail']
    trend_point = db['trend_point']
    another_boards = list(board_detail.find({"board": {"$in": ['猪肉概念']}}))
    for another_board in another_boards:
        total = another_board['codes']
        r = list(trend_point.find(
            {"code": {"$in": total},
             "date": {"$lte": datetime(2022, 9, 16)},
             "update": {"$gte": datetime(2022, 9, 16)},
             "is_in_use":1,
             "trend":"up"
             }))
        pass

if __name__ == "__main__":

    # print(date_util.get_work_day(datetime.now(), 1100))


    from app import application

    application.create_app("infinity")
    # clear_stock_info()
    # trend_data_task()
    # test()
    # rps_test()
    # trend_detail()
