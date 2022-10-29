import numpy as np
import pandas as pd
import math
from decimal import Decimal


def get_rate(a1, a2):
    return Decimal((a2 - a1) / a1 * 100).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")


def get_line(Y=None, X=None):
    """
    根据点获取线
    :param Y:
    :param X:
    :return:
    """
    Y = np.array(Y)

    if X is None:
        X = np.array([i + 1 for i in range(len(Y))])

    A = np.vstack([X, np.ones(len(X))]).T
    m, c = np.linalg.lstsq(A, Y, rcond=None)[0]

    p = "{}X + {} - Y = 0".format(float(str(m)[:6]), c)

    return [m, c]


def get_dis(r, point):
    A = r[0]
    C = r[1]

    d = abs(A * point[0] - point[1] + C) / math.sqrt(math.pow(A, 2) + math.pow(1, 2))
    return d


def get_bot_line(Y):
    """
    获取底部支撑线
    :param Y:
    :return:
    """
    # Y = [1.066, 1.155, 1.251, 1.308, 1.443, 1.648, 1.918, 2.095, 2.157, 2.050, 2.063, 2.182, 2.397, 2.576]
    [m, c] = get_line(Y)

    bot_array = []
    for i, v in enumerate(Y):
        y = m * (i + 1) + c
        # 拟合出一个线段后,获取位于线段底部的点
        if v <= y: bot_array.append([i, v])

    dis = {i: get_dis([m, c], [i + 1, v]) for [i, v] in bot_array}

    new_Y = []
    new_X = []
    for k, v in dis.items():
        # prev = k - 1
        # next = k + 1
        # if prev in dis.keys() and next in dis.keys():
        #     if v > dis[prev] and v > dis[next]:
        new_Y.append(Y[k])
        new_X.append(k + 1)

    [m, c] = get_line(new_Y, new_X)

    return [m, c, new_Y, new_X]


def get_top_line(Y):
    """
    获取顶部支撑线
    :param Y:
    :return: m 斜率,c常量
    """
    # Y = [1.066, 1.155, 1.251, 1.308, 1.443, 1.648, 1.918, 2.095, 2.157, 2.050, 2.063, 2.182, 2.397, 2.576]
    [m, c] = get_line(Y)

    top_array = []
    for i, v in enumerate(Y):
        y = m * (i + 1) + c
        # 拟合出一个线段后,获取位于线段上部的点
        if v >= y: top_array.append([i, v])

    dis = {i: get_dis([m, c], [i + 1, v]) for [i, v] in top_array}

    new_Y = []
    new_X = []
    for k, v in dis.items():
        # prev = k - 1
        # next = k + 1
        # if prev in dis.keys() and next in dis.keys():
        #     if v >= dis[prev] and v >= dis[next]:
        new_Y.append(Y[k])
        new_X.append(k + 1)

    [m, c] = get_line(new_Y, new_X)

    return [m, c, new_Y, new_X]


# d_order = sorted(dis.items(), key=lambda x: x[1], reverse=False)
# print(d_order)


def _trace(x):
    """
    获取角度
    :param x:
    :return:
    """
    # 弧度=角度*Math.PI/180
    return 180 * x / math.pi


def get_reverse_point(points):
    """
    三点确定中间点的斜率情况
    获取反转点
    :param point:
    :return: pos_p  先下后上
             neg_p  先上后下
    """
    pos_p = []
    neg_p = []
    total_p = []

    for i, point in enumerate(points):
        if i == 0 or i == len(points) - 1: continue
        prev, useless = get_line([points[i - 1], points[i]])
        next, useless = get_line([points[i], points[i + 1]])
        if prev >= 0 and next < 0:
            neg_p.append(i)
            total_p.append(i)
        if prev < 0 and next >= 0:
            pos_p.append(i)
            total_p.append(i)

    return pos_p, neg_p, total_p


def get_rate(numerator, denominator, ndigits=2) -> float:
    """
    计算涨幅
    :return:
    """
    return float(Decimal(numerator / denominator * 100).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP"))


def round(v, ndigits=2) -> float:
    return float(Decimal(float(v)).quantize(Decimal(str(pow(10,-ndigits))), rounding="ROUND_HALF_UP"))

def divide(a,b,ndigits=2)->float:
    v = a/b
    return round(v,ndigits)



def get_williams(highest, lowest, close):
    """
    计算威廉指标
    :param highest: n日内最高价
    :param lowest: n日内最低价
    :param close: 当前价格
    :return: 威廉指标
    """
    return (highest - close) / (highest - lowest) * 100

def get_reverse_point(points):
    """
    三点确定中间点的斜率情况
    获取反转点
    :param point:
    :return: pos_p  先下后上
             neg_p  先上后下
    """
    pos_p = []
    neg_p = []
    total_p = []
    point_index = []

    for i, point in enumerate(points):
        if i == 0 or i == len(points) - 1: continue
        prev, useless = get_line([points[i - 1]['value'], points[i]['value']])
        next, useless = get_line([points[i]['value'], points[i + 1]['value']])
        if prev >= 0 and next < 0:
            neg_p.append(i)
            total_p.append(i)
            point_index.append(point['index'])
        if prev < 0 and next >= 0:
            pos_p.append(i)
            total_p.append(i)
            point_index.append(point['index'])

    return pos_p, neg_p, total_p, point_index

def get_top_type(arrays) -> list:
        """
        筛选顶分型
        :return:
        """
        results = []

        for i, item in enumerate(arrays):
            if i == 0:
                # results.append(dict(i=i, v=item))
                results.append(dict(index=i, value=item))
                continue
            if i == len(arrays) - 1:
                pre = results[-1]['value']
                if item > pre:
                    results.append(dict(index=i, value=item))
                continue

            target = item
            pre = arrays[i - 1]
            next = arrays[i + 1]

            if target > pre and target > next:
                # results.append(dict(i=i, v=item))
                results.append(dict(index=i, value=item))
        return results

def get_bottom_type(arrays) -> list:
        """
        筛选底分型
        :param arrays:
        :return:
        """
        results = []

        for i, item in enumerate(arrays):
            if i == 0:
                # results.append(dict(i=i, v=item))
                results.append(dict(index=i, value=item))
                continue
            if i == len(arrays) - 1:
                pre = results[-1]['value']
                if item < pre:
                    results.append(dict(index=i, value=item))
                continue
            target = item
            pre = arrays[i - 1]
            next = arrays[i + 1]

            if target < pre and target <= next:
                # results.append(dict(i=i, v=item))
                results.append(dict(index=i, value=item))

        return results


if __name__ == "__main__":
    # print(_trace(math.atan(0.55)))
    # line = get_line([4.35, 4.48, 4.71, 4.82])
    # d = get_dis(line, [math.sqrt(2), 0])
    # print(d)
    #
    # a = [1.066, 1.155,1.11, 1.251,1.24, 1.308, 1.443, 1.648, 1.918, 2.095, 2.157, 2.050, 2.063, 2.182, 2.397, 2.576,1]
    # get_bot_line(a)
    #
    # pos_p, neg_p,total = get_reverse_point(a)
    # print(total)
    #
    # print(a[total[-1]:])
    # print(a[total[-2]:total[-1]+1])

    # c = [1,2,3,4]
    # x = get_bottom_type(c)
    # a,b,c,d = get_reverse_point(x)

    m, c = get_line([1,2,3,4])
    print(_trace(math.atan(1)))
