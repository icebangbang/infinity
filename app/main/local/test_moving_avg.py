import numpy as np
import matplotlib.pylab as plt
from scipy.interpolate import make_interp_spline


'''
其它的一些知识点：
raise：当程序发生错误，python将自动引发异常，也可以通过raise显示的引发异常
一旦执行了raise语句，raise语句后面的语句将不能执行
'''


def moving_average(interval, windowsize):
    window = np.ones(int(windowsize)) / float(windowsize)
    re = np.convolve(interval, window, 'same')
    return re

def smooth_xy(lx, ly):
    """数据平滑处理

    :param lx: x轴数据，数组
    :param ly: y轴数据，数组
    :return: 平滑后的x、y轴数据，数组 [slx, sly]
    """
    x = np.array(lx)
    y = np.array(ly)
    x_smooth = np.linspace(x.min(), x.max(), 300)
    y_smooth = make_interp_spline(x, y)(x_smooth)
    return x_smooth, y_smooth


def LabberRing():
    # t = np.linspace(-4, 4, 100)  # np.linspace 等差数列,从-4到4生成100个数
    # print('t=', t)
    # # np.random.randn 标准正态分布的随机数，np.random.rand 随机样本数值
    # y = np.sin(t) + np.random.randn(len(t)) * 0.1  # 标准正态分布中返回1个，或者多个样本值
    # print('y=', y)

    t = [1,2,3,4,5,6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    y = [1.53, 2.34, 1.83, 2.66, 1.9, 5.92, 2.04, 7.24, 2.72, 1.10, 4.70]

    plt.plot(t, y, 'k')  # plot(横坐标，纵坐标， 颜色)
    t2,y2 = smooth_xy(t,y)
    y_av = moving_average(y, 5)
    plt.plot(t2, y2, 'b')
    plt.xlabel('Time')
    plt.ylabel('Value')
    # plt.grid()网格线设置
    plt.grid(True)
    plt.show()
    return


LabberRing()  # 调用函数
