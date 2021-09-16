import backtrader as bt
from app.main.stock.ind.kdj import KDJ
from app.main.stock.ind.bollinger import BollingerBandsWidth

class IndTestStrategy(bt.Strategy):
    params = (
        ('maperiod', 5),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # Add a MovingAverageSimple indicator
        # self.kdj = KDJ()
        # self.boll_width = BollingerBandsWidth()

        # Indicators for the plotting show
        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
        #                                     subplot=True)
        # bt.indicators.StochasticSlow(self.datas[0])
        # bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # bt.indicators.ATR(self.datas[0], plot=False)

    def next(self):
        # self.log("{},{},{}".format(self.kdj.K[0],self.kdj.D[0],self.kdj.J[0]))
        # self.log("{} {} {} {}".format(self.boll_width.mid[0],
        #                               self.boll_width.top[0],
        #                               self.boll_width.bot[0],
        #                               self.boll_width.width[0]))

        print('%s' %
              (self.sar[0]))

