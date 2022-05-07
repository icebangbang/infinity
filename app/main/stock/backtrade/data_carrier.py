import backtrader as bt

class PandasDataMore(bt.feeds.PandasData):
    lines = ('prev_close',)  # 要添加的线
    # 设置 line 在数据源上的列位置
    params = (
        ('prev_close', -1),
        ('dtformat', ('%Y-%m-%d')),
    )