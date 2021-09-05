from backtrader import Indicator
from backtrader.indicators.mabase import MovAv


class SampleStandardDeviation(Indicator):
    '''
    计算样本方差
    参照 backtrader.indicators.deviation.StandardDeviation
    backtrader官方使用的是总体方差

    同花顺和东方财富使用的是样本方差,所以这里以主流软件为主
    See:
      - http://en.wikipedia.org/wiki/Standard_deviation
    '''
    alias = ('StdDev',)

    lines = ('stddev',)
    params = (('period', 20), ('movav', MovAv.Simple), ('safepow', True),)

    def _plotlabel(self):
        plabels = [self.p.period]
        plabels += [self.p.movav] * self.p.notdefault('movav')
        return plabels

    def __init__(self):

        mean = self.p.movav(self.data, period=self.p.period)

        meansq = self.p.movav(pow(self.data, 2), period=self.p.period)
        sqmean = pow(mean, 2)

        if self.p.safepow:
            self.lines.stddev = pow(abs(meansq - sqmean)* self.p.period/(self.p.period-1), 0.5)
        else:
            self.lines.stddev = pow(meansq - sqmean, 0.5)