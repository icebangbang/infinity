from datetime import datetime,timedelta

import dateutil
import numpy as np
import scipy
from matplotlib import pyplot as plt
from scipy.signal import argrelextrema, find_peaks
from app.main.db.mongo import db
from app.main.stock.dao import k_line_dao, board_dao
from app.main.stock.service import fund_service
from app.main.stock.service.assist import trend_analysis_helper
from app.main.utils import rolling_window, cal_util, date_util
import pandas as pd
import logging as log

from app.main.utils.date_util import WorkDayIterator

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

    trend_data_list = list(trend_data.find({"industry": industry,
                                            "date": {"$gte": start, "$lte": end},
                                            "trend": "up"}).sort("date", 1))

    df = pd.DataFrame(trend_data_list)
    t = df.date
    x = df.rate

    thresh_bottom = np.mean(x)

    # 寻找普通的高点
    peak_idx, _ = find_peaks(x)
    n_x = [x[idx] for idx in peak_idx]
    thresh_top = np.mean(n_x)
    peak_idx, _ = find_peaks(x, height=thresh_top, distance=10)

    # Find indices of valleys (from inverting the signal)
    valley_idx, _ = find_peaks(-x)
    n_x = [x[idx] for idx in valley_idx]
    thresh_bottom = np.mean(n_x)
    valley_idx, _ = find_peaks(-x, height=-thresh_bottom, distance=10)

    # thresh_top = np.mean(x)
    # thresh_bottom = np.mean(x)
    #
    # # Find indices of peaks
    # peak_idx, _ = find_peaks(x, height=thresh_top, distance=5)
    #
    # # Find indices of valleys (from inverting the signal)
    # valley_idx, _ = find_peaks(-x, height=-thresh_bottom, distance=5)

    # 数据格式转换
    peak_list = _transform(trend_data_list, peak_idx, "top")
    valley_list = _transform(trend_data_list, valley_idx, "bottom")

    # 合并peak和valley,然后根据index进行排序
    peak_list.extend(valley_list)
    sorted_result = sorted(peak_list, key=lambda item: item['index'], reverse=False)
    _set_head(trend_data_list, sorted_result)
    _set_tail(trend_data_list, sorted_result)

    merged_result = []
    index = 0
    while index <= len(sorted_result) - 1:
        element = sorted_result[index]
        trend = element['type']
        temp_list = [element]
        while index <= len(sorted_result) - 1:
            index = index + 1
            try:
                next_element = sorted_result[index]
            except IndexError:
                break
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


def cal_maximum_rollback(start, end, k_line_data_list):
    """
        统计最大回撤
        :return:
        """
    cost = k_line_data_list[0]['close']
    maximum_rollback = 0
    maximum_rollback_start = None
    maximum_rollback_end = None

    k_line_data_dict = {k_line_data['date']: k_line_data for k_line_data in k_line_data_list}

    for cursor in WorkDayIterator(start, end):
        for sub_cursor in WorkDayIterator(cursor, end):
            k_line_data = k_line_data_dict.get(sub_cursor, None)
            if k_line_data is None: continue

            close = k_line_data['close']

            rate = cal_util.get_rate(close - cost, cost)
            if rate < maximum_rollback:
                maximum_rollback = rate
                maximum_rollback_start = cursor
                maximum_rollback_end = sub_cursor
    log.info("{},{},最大回撤:{}".format(maximum_rollback_start, maximum_rollback_end,
                                        maximum_rollback))
    return dict(maximum_rollback=maximum_rollback,
                maximum_rollback_start=maximum_rollback_start,
                maximum_rollback_end=maximum_rollback_end)


def cal_maximum_up(start, end, k_line_data_list):
    """
        统计最大涨幅
        :return:
        """
    cost = k_line_data_list[0]['close']
    maximum_up = 0
    maximum_up_start = None
    maximum_up_end = None

    k_line_data_dict = {k_line_data['date']: k_line_data for k_line_data in k_line_data_list}

    for cursor in WorkDayIterator(start, end):
        for sub_cursor in WorkDayIterator(cursor, end):
            k_line_data = k_line_data_dict.get(sub_cursor, None)
            if k_line_data is None: continue

            close = k_line_data['close']

            rate = cal_util.get_rate(close - cost, cost)
            if rate > maximum_up:
                maximum_up = rate
                maximum_up_start = cursor
                maximum_up_end = sub_cursor
    log.info("{},{},最大涨幅:{}".format(maximum_up_start, maximum_up_end,
                                        maximum_up))
    return dict(maximum_up=maximum_up, maximum_up_start=maximum_up_start, maximum_up_end=maximum_up_end)


def find_stocks(industry, start=None, end=None):
    """
    按照波峰和波谷的提示，筛选出，涨幅最高的，和跌幅最大的股
    :return:
    """
    board_detail = board_dao.get_board_by_name(industry)
    codes = board_detail['codes']
    merged_result = plot_peaks(industry, start, end, False)
    x = rolling_window(merged_result,2)
    while x.hasnext():
        window = next(x)
        a = window[0]
        b = window[1]
        # 上行区间
        if a['type'] == 'bottom' and b['type'] == 'top':
            start_scope = a['date']
            end_scope = b['date']
            k_line_list = k_line_dao.get_k_line_data(start_scope, end_scope, 'day', codes)
            if len(k_line_list) == 0: continue
            # 将数据按照code分组
            df = pd.DataFrame(k_line_list)
            result_list = []
            for code, group in df.groupby("code"):
                # todo 计算最大回撤
                records = group.to_dict("records")
                rollback_dict = cal_maximum_rollback(start_scope, end_scope, records)
                up_dict = cal_maximum_up(start_scope, end_scope, records)

                new_dict = dict(code=code,
                                start_date=records[0]['date'],
                                close=records[0]['close'],
                                start_scope=start_scope,
                                end_scope=end_scope)
                new_dict.update(rollback_dict)
                new_dict.update(up_dict)
                result_list.append(new_dict)
            result_list = sorted(result_list, key=lambda item: (item['maximum_up'], item['maximum_rollback']), reverse=True)
            for result in result_list:
                trend_analysis_helper.analysis_stock_value(result)
                trend_analysis_helper.analysis_price_range(result)


            for result in result_list:
                result['industry'] = industry
                result['up_rate_start'] = a['rate']
                result['trend'] = "up"

                db['stock_training_picker'].update_one({"start_scope":result['start_scope'],
                                                        "code":result['code'],
                                                        "board":industry,
                                                        "trend":"up"},
                                                   {"$set":result},upsert=True)
        # 下行区间
        if a['type'] == 'bottom' and b['type'] == 'top':
            pass

def find_stocks_by_year(board,year):
    start = datetime(year,1,1)
    end = datetime(year,12,31)

    now = date_util.get_start_of_day(datetime.now())
    if end >= now:
        end = now
        start = now-dateutil.relativedelta.relativedelta(years=1)
    find_stocks(board,start,end)




def _transform(trend_data_list, idx_list, type):
    """
    转换数据格式
    :param trend_data_list:
    :param idx_list:
    :param type:
    :return:
    """
    return [dict(index=idx,
                 date=trend_data_list[idx]['date'],
                 rate=trend_data_list[idx]['rate'],
                 type=type
                 ) for idx in idx_list]


def _set_head(trend_data_list, sorted_list):
    """
    重新设置数据的头部
    :return:
    """
    #
    head = trend_data_list[0]
    first = sorted_list[0]
    if head['rate'] >= first['rate']:
        new_head = dict(index=0,
                        date=trend_data_list[0]['date'],
                        rate=trend_data_list[0]['rate'],
                        type='top'
                        )
    else:
        new_head = dict(index=0,
                        date=trend_data_list[0]['date'],
                        rate=trend_data_list[0]['rate'],
                        type='bottom'
                        )
    return sorted_list.insert(0, new_head)


def _set_tail(trend_data_list, sorted_list):
    """
    重新设置数据的尾部
    :return:
    """
    #
    tail = trend_data_list[-1]
    last = sorted_list[-1]
    if tail['rate'] >= last['rate']:
        new_tail = dict(index=len(trend_data_list) - 1,
                        date=trend_data_list[-1]['date'],
                        rate=trend_data_list[-1]['rate'],
                        type='top'
                        )
    else:
        new_tail = dict(index=0,
                        date=trend_data_list[-1]['date'],
                        rate=trend_data_list[-1]['rate'],
                        type='bottom'
                        )
    return sorted_list.append(new_tail)

if __name__ == '__main__':
    # find_stocks("煤炭行业", datetime(2019, 1, 1), datetime(2019, 12, 1))
    # find_stocks("光伏设备", datetime(2022, 1, 1), datetime(2022, 12, 1))
    # plot_peaks("光伏设备", datetime(2019, 1, 1), datetime(2019, 12, 1), True)

    find_stocks_by_year("风电设备", 2019)
    find_stocks_by_year("风电设备", 2020)
    find_stocks_by_year("风电设备", 2021)
    find_stocks_by_year("风电设备",2022)
