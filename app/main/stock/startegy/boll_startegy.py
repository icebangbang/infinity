import backtrader as bt
import logging
from app.main.stock.ind.bollinger import BollingerBandsPct
from datetime import datetime
from app.main.utils import date_util

class BollBStartegy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        logging.info('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, house):
        self.inds = dict()
        self.house = house

        for i, d in enumerate(self.datas):
            code = d._name
            house[code] = dict()
            boll_pctb = BollingerBandsPct()
            house[code]['pctb'] = boll_pctb

    def next(self):
        for i, d in enumerate(self.datas):
            code = d._name
            day_time = datetime.combine(d.datetime.date(0),datetime.min.time())
            #day = date_util.get_days_between(datetime.now(),day_time) < 20

            day = d.buflen() -len(d)

            if day >= 18+1: continue # 只考虑20日内的数据
            flag = True

            if d.close[0] > self.house[code]['pctb'].mid[0]:
                if flag is True: flag=False

            self.house[code]['in_need'] = flag
            # 最近20日,处于布林轨道下轨内



