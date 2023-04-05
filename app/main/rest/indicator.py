import collections
from datetime import datetime

import pandas as pd
from flask import request

from app.main.db.mongo import db
from app.main.stock.chart import chart_instance_dict
from app.main.stock.dao import stock_dao
from app.main.utils import date_util
from app.main.utils import restful
from . import rest


@rest.route("/indicator/ppi", methods=['get'])
def get_ppi():
    """
    ppi 数据展示
    :return:
    """
    start = datetime(2020, 1, 1)
    ppi = db['ppi']
    ppi_list = list(ppi.find({"date": {"$gte": start}}).sort("_id", -1))

    cpi = db['cpi']
    cpi_list = list(cpi.find({"date": {"$gte": start}}).sort("_id", -1))

    # pmi = db['pmi']
    # pmi_list = list(pmi.find({"date": {"$gte": start}}).sort("_id", -1))

    date = []
    current = []
    grace = []
    accum = []
    cpi = []
    # pmi = []

    for i, p in enumerate(ppi_list):
        date.append(date_util.date_time_to_str(p['date'], fmt='%Y-%m'))
        current.append(float(p['current']))
        grace.append(float(p['grace']))
        accum.append(float(p['accum']))
        try:
            cpi.append(float(cpi_list[i]['country_current']))
        except:
            pass
        # pmi.append(float(pmi_list[i]['zzy_value']))

    return restful.response(data=dict(date=date, current=current, grace=grace,
                                      accum=accum, cpi=cpi))


@rest.route("/indicator/pmi", methods=['get'])
def get_pmi():
    """
    pmi数据展示
    :return:
    """
    start = datetime(2006, 1, 1)
    ppi = db['pmi']
    ppi_list = list(ppi.find({"date": {"$gte": start}}).sort("_id", 1))

    date = []
    zzy = []
    fzzy = []

    for i, p in enumerate(ppi_list):
        date.append(date_util.date_time_to_str(p['date'], fmt='%Y-%m'))
        zzy.append(p.get('zzy_value', None))
        fzzy.append(p.get('fzzy_value', None))

    return restful.response(data=dict(date=date, zzy=zzy, fzzy=fzzy))


@rest.route("/indicator/sow", methods=['get'])
def get_sow_data():
    """
    母猪数据展示
    :return:
    """
    pig_data = db['pig_data']
    sow_data_list = list(pig_data.find({"name": "能繁母猪存栏"}).sort("_id", 1))

    num = []
    tb = []
    hb = []
    date = []
    for i, sow in enumerate(sow_data_list):
        num.append(sow["num"])
        tb.append(sow["tb"].strip('%'))
        hb.append(sow["hb"].strip('%'))
        date.append(date_util.date_time_to_str(sow['date'], fmt='%Y-%m'))
    return restful.response(data=dict(date=date, num=num, tb=tb, hb=hb))


@rest.route("/indicator/chart", methods=['get'])
def chart_display():
    """
    抽象图表展示层,根据名字定位到具体业务
    :return:
    """
    name = request.args.get("name")
    chart_instance = chart_instance_dict[name]
    data = chart_instance.generate(**request.args)

    return restful.response(data=data)


@rest.route("/indicator/marketStatus/current", methods=['get'])
def current_market_status():
    """
    当前市场情况展示
    """
    market_status = db['market_status']
    latest_point = market_status.find_one({}, sort=[('date', -1)])
    result = latest_point['distribution']
    result['rateMedian'] = latest_point['rate_median']

    return restful.response(data=result)


@rest.route("/indicator/upLimit", methods=['get'])
def upLimit_detail():
    """
    当前涨停情况展示
    """

    date = date_util.get_latest_work_day()
    stock_feature = db['stock_feature']
    results = list(stock_feature.find({"features.cont_up_limit_count": {"$gte": 1},
                                       "date": date}))
    codes = [result['code'] for result in results]

    stock_map = stock_dao.get_stock_detail(codes)

    stocks = [dict(name=result['name'],
                   code=result['code'],
                   cont_up_limit_count=result['features']['cont_up_limit_count']) for result in results]
    df = pd.DataFrame(stocks)
    df['cut'] = pd.cut(df.cont_up_limit_count, bins=[0, 1, 2, 3, 4, 5, 100], labels=["1", "2", "3", "4", "5", ">=6"],
                       include_lowest=False)

    group_result = []
    for cut, group in df.groupby('cut'):
        records = group.to_dict('records')

        industries = []
        for record in records:
            stock = stock_map[record['code']]

            if "industry" in stock.keys():
                industries.append(stock['industry'])
        counter = collections.Counter(industries)

        item = dict(time=cut, stocks=[r['name'] for r in records],
                    industries=counter.most_common(len(counter)))

        group_result.append(item)

    # group_result = [dict(time=cut, stocks= [ r['name'] for r in group.to_dict('records')])
    #                 for cut, group in df.groupby('cut')]

    return restful.response(data=group_result)


@rest.route("/indicator/upLimitBack", methods=['get'])
def upLimit_back_detail():
    """
    涨停预备队
    """

    date = date_util.get_latest_work_day()
    stock_feature = db['stock_feature']
    results = list(stock_feature.find({"features.continuous_up_limit_stop": True,
                                       "features.continuous_up_limit_count_before": {"$gte": 1},
                                       "date": date}))

    stocks = [dict(name=result['name'],
                   code=result['code'],
                   continuous_up_limit_count_before=result['features']['continuous_up_limit_count_before']) for result
              in results]

    codes = [result['code'] for result in results]

    stock_map = stock_dao.get_stock_detail(codes)

    df = pd.DataFrame(stocks)
    df['cut'] = pd.cut(df.continuous_up_limit_count_before, bins=[0, 1, 2, 3, 4, 5, 100],
                       labels=["1", "2", "3", "4", "5", ">=6"],
                       include_lowest=False)

    group_result = []
    for cut, group in df.groupby('cut'):
        records = group.to_dict('records')

        industries = []
        for record in records:
            stock = stock_map[record['code']]

            if "industry" in stock.keys():
                industries.append(stock['industry'])
        counter = collections.Counter(industries)

        item = dict(time=cut, stocks=[r['name'] for r in records],
                    industries=counter.most_common(len(counter)))

        group_result.append(item)

    return restful.response(data=group_result)
