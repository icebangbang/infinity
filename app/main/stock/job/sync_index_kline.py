from app.main.stock.service import stock_index_service
from datetime import datetime

from app.main.utils import date_util

def sync():
    # 上证,深证,创业板
    id_list = ["sh000001", "zs399001", "zs399006","BDI","zs399106"]

    now = datetime.now()
    start = date_util.get_work_day(now, 250)

    for code in id_list:
        print("同步{}".format(code))
        stock_index_service.sync_index_data(code,
                                            date_util.dt_to_str(start),
                                            date_util.dt_to_str(now))
