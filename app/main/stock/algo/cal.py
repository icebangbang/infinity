import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math


def predict(Y=None, X=None):
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
    # Y = [1.066, 1.155, 1.251, 1.308, 1.443, 1.648, 1.918, 2.095, 2.157, 2.050, 2.063, 2.182, 2.397, 2.576]
    [m, c] = predict(Y)

    bot_array = []
    for i, v in enumerate(Y):
        y = m * (i + 1) + c
        if v < y: bot_array.append([i, v])

    dis = {i: get_dis([m, c], [i + 1, v]) for [i, v] in bot_array}

    new_Y = []
    new_X = []
    for k, v in dis.items():
        prev = k - 1
        next = k + 1
        if prev in dis.keys() and next in dis.keys():
            if v > dis[prev] and v > dis[next]:
                new_Y.append(Y[k])
                new_X.append(k + 1)

    [m, c] = predict(new_Y, new_X)

    return [m, c]

    # d_order = sorted(dis.items(), key=lambda x: x[1], reverse=False)
    # print(d_order)


def trace(x):
    # 弧度=角度*Math.PI/180
    return 180 * x / math.pi


if __name__ == "__main__":
    print(trace(math.atan(0.55)))
    line = predict([1, 2, 3, 4, 5])
    d = get_dis(line, [math.sqrt(2), 0])
    print(d)

    get_bot_line([1.066, 1.155, 1.251, 1.308, 1.443, 1.648, 1.918, 2.095, 2.157, 2.050, 2.063, 2.182, 2.397, 2.576])
