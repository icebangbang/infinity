from app.main.stock.job import bt_runner
from datetime import datetime
from app.main.stock.sub_startegy.up_sma import UpSma
from app.main.stock.sub_startegy.down_bolling import DownBolling
from app.main.stock.sub_startegy.kdj_golden import KdjGolden
from app.main.stock.sub_startegy.heavy_vol import HeavyVol
from app.main.stock.sub_startegy.bolling_width import BollingWidth
from app.main.stock.sub_startegy.up_bolling import UpBolling

from_date = datetime(2021, 8, 1)
to_date = datetime(2021, 9, 8)

concept_names = []
sub_st = [UpSma,UpBolling]
kwargs = {"ma_period":1,
          "ma_match_num":1,
          "up_bot_bolling_period":1}

bt_runner.run(from_date, to_date, concept_names=concept_names,sub_st=sub_st,**kwargs)
