from datetime import datetime

import numpy as np
from matplotlib import pyplot as plt

from app.main.db.mongo import db


def AMPD(data):
    """
    实现AMPD算法
    :param data: 1-D numpy.ndarray
    :return: 波峰所在索引值的列表
    """
    p_data = np.zeros_like(data, dtype=np.int32)
    count = data.shape[0]
    arr_rowsum = []
    for k in range(1, count // 2 + 1):
        row_sum = 0
        for i in range(k, count - k):
            if data[i] > data[i - k] and data[i] > data[i + k]:
                row_sum -= 1
        arr_rowsum.append(row_sum)
    min_index = np.argmin(arr_rowsum)
    max_window_length = min_index
    for k in range(1, max_window_length + 1):
        for i in range(k, count - k):
            if data[i] > data[i - k] and data[i] > data[i + k]:
                p_data[i] += 1
    return np.where(p_data == max_window_length)[0]

def vis():
    trend_data = db['trend_data']

    trend_data_list = list(trend_data.find({"industry": "光伏设备",
                                            "date": {"$gte": datetime(2022, 1, 1), "$lte": datetime(2022, 12, 1)},
                                            "trend": "up"}).sort("date",1))
    rate_list = [data['rate'] for data in trend_data_list]

    for i in range(len(rate_list)):
        print(rate_list[i])
        if rate_list[i] == rate_list[i - 1]:
            rate_list[i] = rate_list[i]-0.1


    y = np.array(rate_list)



    plt.plot(range(len(y)), y)
    px = AMPD(y)
    plt.scatter(px, y[px], color="red")

    plt.show()

vis()