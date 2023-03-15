"""
寻找趋势变化的分类，观察
"""

from datetime import datetime

from app.main.db.mongo import db

trend_point_set = db['trend_point']

trend_chain = ['up', 'enlarge', 'down']

trend_chain_group = {
    "UP->ENLARGE->DOWN": ['up', 'enlarge', 'down'],
    "UP->CONV->DOWN": ['up', 'convergence', 'down'],
}

for k,chain in trend_chain_group.items():

    r = trend_point_set.find({"trend": chain[2],
                              'prev_trend_1': chain[1],
                              "prev_trend_2": chain[0],
                              'date': {"$gte": datetime(2023, 2, 1)}}).count()

    print(k,r)
