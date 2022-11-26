from datetime import datetime

import numpy as np
import pandas as pd
import scipy
from matplotlib import pyplot as plt
from scipy.signal import argrelextrema, find_peaks
from app.main.db.mongo import db

def plot_peaks():
    trend_data = db['trend_data']

    trend_data_list = list(trend_data.find({"industry": "光伏设备",
                                            "date": {"$gte": datetime(2022, 1, 1), "$lte": datetime(2022, 12, 1)},
                                            "trend": "up"}))
    rate_list = [data['rate'] for data in trend_data_list]
    x = np.array(rate_list)
    index_data, _ = scipy.signal.find_peaks(
        x,
        prominence=0.8
    )
    print(index_data)
    import matplotlib.pyplot as plt
    plt.plot(x)
    plt.scatter(
        argrelextrema(x, np.greater),
        x[argrelextrema(x, np.greater)],
        c='red'
    )
    plt.show()

trend_data = db['trend_data']

def func2():
    trend_data = db['trend_data']

    trend_data_list = list(trend_data.find({"industry": "煤炭行业",
                                            "date": {"$gte": datetime(2022, 1, 1), "$lte": datetime(2022, 12, 1)},
                                            "trend": "up"}))
    df = pd.DataFrame(trend_data_list)
    t = df.date
    x = df.rate

    # rate_list = [data['rate'] for data in trend_data_list]
    # x = np.array(rate_list)
    thresh_top = np.mean(x) + 1 * np.std(x)
    thresh_bottom = np.mean(x) - 1 * np.std(x)
    # (you may want to use std calculated on 10-90 percentile data, without outliers)

    # Find indices of peaks
    peak_idx, _ = find_peaks(x, height=thresh_top,distance=10)

    # Find indices of valleys (from inverting the signal)
    valley_idx, _ = find_peaks(-x, height=-thresh_bottom,distance=10)

    # Plot signal
    # plt.figure(figsize=(14, 12))
    plt.plot(t, x, color='b', label='data')
    plt.scatter(t, x, s=10, c='b', label='value')

    # Plot threshold
    plt.plot([min(t), max(t)], [thresh_top, thresh_top], '--', color='r', label='peaks-threshold')
    plt.plot([min(t), max(t)], [thresh_bottom, thresh_bottom], '--', color='g', label='valleys-threshold')

    # Plot peaks (red) and valleys (blue)
    plt.plot(t[peak_idx], x[peak_idx], "x", color='r', label='peaks')
    plt.plot(t[valley_idx], x[valley_idx], "x", color='g', label='valleys')

    plt.xticks(rotation=45)
    plt.ylabel('value')
    plt.xlabel('timestamp')
    plt.title(f'data over time for username=target')
    plt.legend(loc='upper left')
    plt.gcf().autofmt_xdate()
    plt.show()

func2()
