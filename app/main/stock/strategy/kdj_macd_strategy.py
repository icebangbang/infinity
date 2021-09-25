import backtrader as bt

from app.main.stock.ind.kdj import KDJ_MACD,KDJ


class KdjMacdStrategy(bt.Strategy):
    params = (
        ('maperiod', 5),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, company):

        # self.ma60 = bt.indicators.SimpleMovingAverage(
        #     self.data, period=60)
        self.kdj_macd = KDJ(df =self.data)

        self.company = company
        self.k_hit= 1

        self.l.high = bt.indicators.Highest(self.data.high, period=9)
        self.l.low = bt.indicators.Lowest(self.data.low, period=9)
        self.l.rsv = 100 * bt.DivByZero(self.data_close - self.l.low, self.l.high - self.l.low, zero=None)
        self.l.K = bt.indicators.EMA(self.l.rsv, period=2)
        self.l.D = bt.indicators.EMA(self.l.K, period=2)
        self.l.J = 3 * self.l.K - 2 * self.l.D
        self.kdj = KDJ(self.data)


    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close,{} {}'.format(self.kdj.K[0]-self.kdj.D[0],self.kdj.K[0]))
        # sma60 = self.ma60
        data = self.data



        # c1 = True
        # # c1 = sma60[0] >= sma60[-1] and sma60[-1] >= sma60[-2]
        #
        # # day = data.buflen() - len(data)
        #
        # k_hit = self.k_hit
        # k_hit = k_hit-1
        #
        # if K[0] < 25: k_hit = 15
        #
        # c2 = k_hit > 0
        #
        # c3 = self.KMhisto[0] >= 0 and self.KMhisto[-1] < 0
        #
        # hit = c1 and c2 and c3
        # # self.log("{}".format(hit))
        #
        # self.company.hit = hit
        #
        # if hit:
        #     print(123)


        # Check if we are in the market
        # if not self.position:
        #
        #     # Not yet ... we MIGHT BUY if ...
        #     if self.data[0] > self.sma[0]:
        #         # BUY, BUY, BUY!!! (with all possible default parameters)
        #         self.log('BUY CREATE, %.2f' % self.dataclose[0])
        #
        #         # Keep track of the created order to avoid a 2nd order
        #         self.order = self.buy()
        #
        # else:
        #
        #     if self.dataclose[0] < self.sma[0]:
        #         # SELL, SELL, SELL!!! (with all possible default parameters)
        #         self.log('SELL CREATE, %.2f' % self.dataclose[0])
        #
        #         # Keep track of the created order to avoid a 2nd order
        #         self.order = self.sell()
