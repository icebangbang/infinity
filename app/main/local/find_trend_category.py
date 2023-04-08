"""
寻找趋势变化的分类，观察
"""

from datetime import datetime

from app.main.db.mongo import db

trend_point_set = db['trend_point']

trend_chain = ['up', 'enlarge', 'down']

trend_chain_group = {
    "UP->ENLARGE->DOWN": dict(chain=['up', 'enlarge', 'down'], type="下行"),
    "UP->CONV->DOWN": dict(chain=['up', 'convergence', 'down'], type="下行"),
    "UP->ENLARGE->UP": dict(chain=['up', 'enlarge', 'up'], type="上行"),
    "UP->CONV->UP": dict(chain=['up', 'convergence', 'up'], type="上行"),
    "DOWN->CONV->DOWN": dict(chain=['down', 'convergence', 'down'], type="下行"),
    "DOWN->ENLARGE->DOWN": dict(chain=['down', 'enlarge', 'down'], type="下行"),
    "DOWN->CONV->UP": dict(chain=['down', 'convergence', 'up'], type="上行"),
    "DOWN->ENLARGE->UP": dict(chain=['down', 'enlarge', 'up'], type="上行"),

    "CONV->UP->CONV": dict(chain=['convergence', 'up', 'convergence'], type="收敛"),
    "CONV->UP->ENLARGE": dict(chain=['convergence', 'up', 'enlarge'], type="放大"),
    "CONV->DOWN->CONV": dict(chain=['convergence', 'down', 'convergence'], type="收敛"),
    "CONV->DOWN->ENLARGE": dict(chain=['convergence', 'down', 'enlarge'], type="放大"),
    "ENLARGE->UP->CONV": dict(chain=['enlarge', 'up', 'convergence'], type="收敛"),
    "ENLARGE->UP->ENLARGE": dict(chain=['enlarge', 'up', 'enlarge'], type="放大"),
    "ENLARGE->DOWN->CONV": dict(chain=['enlarge', 'down', 'convergence'], type="收敛"),
    "ENLARGE->DOWN->ENLARGE": dict(chain=['enlarge', 'down', 'enlarge'], type="放大"),

}

normal = 1
temp = 3

# for k, item in trend_chain_group.items():
#     chain = item['chain']
date = datetime(2023, 4, 7)
results = list(trend_point_set.find(
    {"date": {"$lte": date},
     "update": {"$gte": date},
     "industry": "电池",
     "is_in_use": 1,
     "trend_type": {"$in": [normal, temp]},
     # "trend": chain[2],
     # "prev_trend_1": chain[1],
     # "prev_trend_2": chain[0]
     })
)

# names = [result['name'] for result in results]
import pandas as pd

groups = pd.DataFrame(results).groupby(['prev_trend_2', 'prev_trend_1', 'trend'])
for key, group_items in groups:
    print(key, ",".join([item['name'] for item in group_items.to_dict(orient="records")]))
