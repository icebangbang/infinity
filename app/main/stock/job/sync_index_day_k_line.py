from app.main.stock.service import stock_index_service
from datetime import datetime

from app.main.utils import date_util

id_list = ["sh000001", "zs399001"]

# 删除数据
stock_index_service.clear_index_data()

now = datetime.now()
start, now = date_util.get_work_day(now, 250)

for code in id_list:
    stock_index_service.sync_index_data(code,
                                        date_util.dt_to_str(start),
                                        date_util.dt_to_str(now))
