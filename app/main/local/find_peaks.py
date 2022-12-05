from datetime import datetime
import numpy as np
import pandas as pd
import scipy
from matplotlib import pyplot as plt
from scipy.signal import argrelextrema, find_peaks
from app.main.db.mongo import db
from app.main.utils import hn_wrapper


def transform(trend_data_list, idx_list, type):
    return [dict(index=idx,
                 date=trend_data_list[idx]['date'],
                 rate=trend_data_list[idx]['rate'],
                 type=type
                 ) for idx in idx_list]


def plot_peaks(industry, start=None, end=None, show_plot=True):
    """
    根据顶和底，拆分得出上行的区间以及下行的区间
    因为每个年份，每个板块的表现也不一样，所以需要根据年份来制定顶部和底部
    该方法用于辅助寻找主升和主跌区间内，对应行业的个股，帮助寻找在上行和下行区间，个股表现出的一些特性
    :param industry: 行业
    :param start: 开始时间
    :param end: 结束时间
    :return:
    """
    trend_data = db['trend_data']

    industry = "光伏设备"
    start = datetime(2019, 1, 1)
    end = datetime(2019, 12, 1)
    trend_data_list = list(trend_data.find({"industry": industry,
                                            "date": {"$gte": start, "$lte": end},
                                            "trend": "up"}).sort("date", 1))

    df = pd.DataFrame(trend_data_list)
    t = df.date
    x = df.rate

    thresh_top = np.mean(x) + 1 * np.std(x)
    thresh_bottom = np.mean(x) - 1 * np.std(x)

    # Find indices of peaks
    peak_idx, _ = find_peaks(x, height=thresh_top, distance=5)

    # Find indices of valleys (from inverting the signal)
    valley_idx, _ = find_peaks(-x, height=-thresh_bottom, distance=5)

    peak_list = transform(trend_data_list, peak_idx, "top")
    valley_list = transform(trend_data_list, valley_idx, "bottom")

    # 合并peak和valley,然后根据index进行排序
    peak_list.extend(valley_list)
    sorted_result = sorted(peak_list, key=lambda item: item['index'], reverse=False)

    merged_result = []
    index = 0
    while index < len(sorted_result) - 1:
        element = sorted_result[index]
        trend = element['type']
        temp_list = [element]
        while index < len(sorted_result) - 1:
            index = index + 1
            next_element = sorted_result[index]
            if trend == next_element['type']:
                temp_list.append(next_element)
            else:
                break

        is_reverse = True if trend == 'top' else False
        r = sorted(temp_list, key=lambda item: (item['rate'], item['date']), reverse=is_reverse)
        merged_result.append(r[0])

    peak_idx = [merged['index'] for merged in merged_result if merged['type'] == 'top']
    valley_idx = [merged['index'] for merged in merged_result if merged['type'] == 'bottom']

    if show_plot:
        plt.plot(t, x, color='b', label='data')
        plt.scatter(t, x, s=10, c='b', label='value')
        # Plot threshold
        plt.plot([min(t), max(t)], [thresh_top, thresh_top], '--', color='r', label='peaks-threshold')
        plt.plot([min(t), max(t)], [thresh_bottom, thresh_bottom], '--', color='g', label='valleys-threshold')

        # Plot peaks (red) and valleys (blue)
        plt.plot(t[peak_idx], x[peak_idx], "x", color='r', label='peaks')
        plt.plot(t[valley_idx], x[valley_idx], "x", color='g', label='valleys')

        plt.xticks(rotation=100)
        plt.ylabel('value')
        plt.xlabel('timestamp')
        plt.title(f'data over time for username=target')
        plt.legend(loc='upper left')
        plt.gcf().autofmt_xdate()
        plt.show()
    else:
        return merged_result


def find_stocks(industry, start=None, end=None):
    """
    按照波峰和波谷的提示，筛选出，涨幅最高的，和跌幅最大的股
    :return:
    """
    merged_result = plot_peaks(industry, start, end)
    x = hn_wrapper(merged_result)
    while x.hasnext():
        print(next(x))


def func2():
    trend_data = db['trend_data']

    trend_data_list = list(trend_data.find({"industry": "煤炭行业",
                                            "date": {"$gte": datetime(2019, 1, 1), "$lte": datetime(2022, 12, 1)},
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
    peak_idx, _ = find_peaks(x, height=thresh_top, distance=10)

    # Find indices of valleys (from inverting the signal)
    valley_idx, _ = find_peaks(-x, height=-thresh_bottom, distance=10)

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


plot_peaks("煤炭行业")
