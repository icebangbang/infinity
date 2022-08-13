from app.main.db.mongo import db
from app.main.stock.job import job_config
from app.main.utils import simple_util

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
    method.apply_async(kwargs=dict(reuild_data=1))

if __name__ == "__main__":
    from app import application
    application.create_app("development")
    # clear_stock_info()
    test()