import backtrader as bt
import logging
from app.main.stock.ind.bollinger import BollingerBandsPct
from datetime import datetime
from app.main.utils import date_util

class Sma5Startegy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        logging.info('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, house):
        self.house = house

        for i, d in enumerate(self.datas):
            code = d._name

            house[code] = dict()
            self.log(code)
            house[code]['sma5'] = bt.indicators.SimpleMovingAverage(
                d, period=5)


    def next(self):
        for i, d in enumerate(self.datas):
            code = d._name

            day = d.buflen() -len(d)
            self.log(self.house[code]['sma5'][0])
            if day >= 5: continue # 只考虑5交易日内的数据

            count = self.house[code].get('sma5_up_count',0)
            if d.close[0] > self.house[code]['sma5'][0]:
                count=count+1

            self.house[code]['sma5_up_count'] = count
            # 最近5日,处于5日线以上的次数



