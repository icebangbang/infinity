from app.main.stock.dao import board_dao
from app.main.stock.job import bt_runner
from datetime import datetime

from app.main.stock.service import board_service, stock_service
from app.main.stock.sub_startegy.up_sma import UpSma
from app.main.stock.sub_startegy.down_bolling import DownBolling, CloseMidBolling,CloseBotBolling
from app.main.stock.sub_startegy.kdj_golden import KdjGolden
from app.main.stock.sub_startegy.heavy_vol import HeavyVol
from app.main.stock.sub_startegy.bolling_width import BollingWidth
from app.main.stock.sub_startegy.up_bolling import UpBolling
from app.main.stock.sub_startegy.k_type import DojiType

"""
概念板块轮动选股
"""
concept_names = None
from_date = datetime(2021, 8, 1)
to_date = datetime(2021, 9, 13)
data = board_service.get_board_k_line(from_date, to_date, concept_names)

sub_st = [UpSma]
kwargs = {"ma_period": 17,
          "ma_match_num": 17,
          "up_mid_bolling_period": 1}

matched_list = bt_runner.run(from_date, to_date, daily_price=data, key="name", sub_st=sub_st, **kwargs)
print(matched_list)
# for matched in matched_list:
#     stock_codes = board_dao.get_stock_bt_board(matched)
#     stock_service.publish(2,20,stock_codes)
