"""
boll布林轨道
"""
# 导入及处理数据
import pandas as pd
import numpy as np
# 绘图
import matplotlib.pyplot as plt
# 设置图像标签显示中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
import matplotlib as mpl
# 解决一些编辑器(VSCode)或IDE(PyCharm)等存在的图片显示问题，
# 应用Tkinter绘图，以便对图形进行放缩操作
mpl.use('TkAgg')




stock_code = 'sh600519'
# 绘制数据的规模
scale = 500
# df = import_csv(stock_code)[-scale:]

def get_boll(df,time_period=20,stdev_factor = 2):
    """
    :param df:
    :param time_period:  SMA的计算周期，默认为20
    :param stdev_factor: 上下频带的标准偏差比例因子
    :return:
    """

    df.rename(columns={
        'date': 'date',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume'
    },inplace=True)

    df['mid'] = df['close'].rolling(20).mean() #中位线
    df['tmp2'] = df['close'].rolling(20).std()
    df['top'] = df['mid'] + 2 * df['tmp2'] # 阻力线
    df['bottom'] = df['mid'] - 2 * df['tmp2'] # 支撑线