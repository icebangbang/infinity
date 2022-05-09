from app.main.stock.dao import board_dao
from app.main.stock.job import bt_runner
from datetime import datetime

from app.main.stock.service import board_service, stock_service, stock_index_service
from app.main.stock.sub_startegy.up_sma import UpSma

"""
中长期(Medium&LongTerm)指数强弱判断
"""
concept_names = None
from_date = datetime(2021, 3, 1)
to_date = datetime(2021, 9, 13)
data = stock_index_service.get_index_k_line(from_date, to_date)
data = data.set_index("date", drop=False)

sub_st = []
kwargs = {"ma_period": 17,
          "ma_match_num": 17,
          "up_mid_bolling_period": 1}

matched_list = bt_runner.run(from_date, to_date, daily_price=data, key="code", sub_st=sub_st, **kwargs)
print(matched_list)
# for matched in matched_list:
#     stock_codes = board_dao.get_stock_bt_board(matched)
#     stock_service.publish(2,20,stock_codes)
