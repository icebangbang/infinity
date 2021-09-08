from app.main.stock.dao import stock_dao
from app.main.stock.job import bt_runner
from datetime import datetime

from_date = datetime(2021, 8, 1)
to_date = datetime(2021, 9, 8)

codes = []
concept = ""

if concept is not None:
    codes = stock_dao.get_stock_detail(concept)

bt_runner.run(from_date, to_date, codes)
