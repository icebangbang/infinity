import backtrader as bt
import pandas as pd
import array


class KDJ(bt.Indicator):
    # 定义KDJ lines，类中可以使用self.lines.K进行访问，也可以使用self.l.K进行访问
    # 注意以下self.lines.K是linebuffer类型，在init中使用self.lines.K，而在next中就需要使用
    # self.lines.K[index]的形式
    lines = ('K', 'D', 'J')

    # kdj周期参数定义，可以使用self.params.fastk_period的形式访问，同样也可以按照self.p.fastk_period的形式访问
    # params = (('fastk_period', 9),('slowk_period', 3),('slowd_period', 3) )

    def __init__(self, **kwargs):
        super(KDJ, self).__init__()
        # 将策略传入的周期参数进行赋值
        # self.params.fastperiod=fastperiod
        # self.params.slowperiod=slowperiod
        # self.params.signalperiod=signalperiod
        # 组装变量
        fastk_period = None
        slowk_period = None
        slowd_period = None
        keys = kwargs.keys()
        for k in keys:
            if k == 'fastk_period':
                fastk_period = kwargs[k]
            if k == 'slowk_period':
                slowk_period = kwargs[k]
            if k == 'slowd_period':
                slowd_period = kwargs[k]

        # 将数据转成DataFrame类型，且包含最低价、最高价及收盘价
        df = pd.DataFrame(pd.Series(self.data.close.array), columns=['close'])
        df['high'] = pd.Series(self.data.high.array)
        df['low'] = pd.Series(self.data.low.array)
        # 计算kdj
        k, d, j = self.calc_kdj(df,
                                fastk_period=fastk_period or 9,
                                slowk_period=slowk_period or 3,
                                slowd_period=slowd_period or 3)
        # 将序列赋值给lines的array,在Strategy中可以通过访问lines进行访问下面数据
        self.lines.K.array = array.array(str('d'), list(k.values))
        self.lines.D.array = array.array(str('d'), list(d.values))
        self.lines.J.array = array.array(str('d'), list(j.values))

    def calc_kdj(self, df, fastk_period=9, slowk_period=3, slowd_period=3, fillna=True):
        '''
        根据传入的最高价、最低价、收盘价计算KDJ指标
        参数:
        df:pandas的DataFrame类型，需要包含最低价、最高价及收盘价
        fastk_period:RSV中日期间隔 int 类型。默认为9日
        slowk_period:K线指标日期间隔 int类型。默认为3天
        slowd_period:D线指标日期间隔 int类型。默认为3天
        fillna:bool类型，默认为False。为True时，在计算RSV的最高价(或最低价)的最大值(或最小值)过程中如果存在Nan数据将被传入的df中的最大值或最小值填充
        '''
        # 检查传入的参数是否是pandas的DataFrame类型
        if not isinstance(df, pd.DataFrame):
            raise Exception("传入的参数不是pandas的DataFrame类型!")
        # 检查传入的df是否存在high、low、close三列，不存在报错
        if ('high' not in df.columns) or ('low' not in df.columns) or (
                'close' not in df.columns):
            # 抛出异常
            raise Exception("传入的参数不存在最高价、最低价、收盘价中的一个或几个!")
        # 计算指定日期间隔内的最低价的最小值
        low_list = df['low'].rolling(fastk_period, min_periods=fastk_period).min()
        # 将NAN填充成现有数据中的最小值
        if fillna is True:
            low_list.fillna(value=df['low'].expanding().min(), inplace=True)
        # 计算指定日期间隔的最高阶的最大值
        high_list = df['high'].rolling(fastk_period, min_periods=fastk_period).max()
        # 将NAN填充成现有数据中的最大值
        if fillna is True:
            high_list.fillna(value=df['high'].expanding().max(), inplace=True)
        # 计算RSV （国泰君安中的RSV公式RSV:=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100;）
        # RSV赋值:(收盘价-N日内最低价的最低值)/(N日内最高价的最高值-N日内最低价的最低值)*100
        rsv = (df['close'] - low_list) / (high_list - low_list) * 100

        k = rsv.ewm(com=slowk_period-1,adjust=False).mean() # rsv针对slowk_period参数求移动权重平均数

        d = k.ewm(com = slowd_period-1,adjust=False).mean()  # k针对slowd_period参数求移动权重平均数当,adjust为False时，以递归方式计算加权平均值

        j = 3 * k - 2 * d
        return (k, d, j)


class KDJ_MACD(KDJ):
    alias = ('KdjMacdHistogram',)
    lines = ('KMhisto',)
    plotlines = dict(histo=dict(_method='bar', alpha=0.50, width=1.0))

    def __init__(self,**kwargs):
        super(KDJ_MACD, self).__init__(**kwargs)
        self.lines.KMhisto = 2 * (self.lines.K - self.lines.D)
