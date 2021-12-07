from app.main.utils import restful
from . import rest
from app.main.task import demo
from app.main.task import board_task
from app.main.db.mongo import db
import pandas as  pd
from datetime import timedelta
from flask import request


@rest.route("/board/rank", methods=['get'])
def get_board():
    set = db["board_k_line"]
    board_type = int(request.args.get("type",2))

    latest = set.find_one({}, sort=[("date", -1)])
    date = latest['date']

    total = list(set.find({"date": {"$lte": date, "$gte": date - timedelta(days=1)}, "type": board_type}))

    df_total = pd.DataFrame(total)

    results = []
    for name, group in df_total.groupby("name"):
        latest_close = None
        first_close = None
        item = None

        if len(group) != 1:
            i = 0
            for index, line in group.iterrows():
                if i == 0:
                    first_close = line['close']
                if i == len(group) - 1:
                    latest_close = line['close']
                i = i + 1
            inc_rate = round((latest_close - first_close) / first_close * 100, 2)
            item = dict(name=name, rate=inc_rate)
        else:
            line = group.iloc[0]
            inc_rate = round((line['close'] - line['open']) / line['open']* 100, 2)

            item = dict(name=name, rate=inc_rate)
        results.append(item)

    results = sorted(results, key=lambda x: x['rate'], reverse=True)

    return restful.response(results)
