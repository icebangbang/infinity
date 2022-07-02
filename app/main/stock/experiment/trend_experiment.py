from app.main.db.mongo import db
from datetime import datetime

from app.main.utils import date_util
import pandas as pd


def run_day():
    r = db.trade_point.find(
        {"update": date_util.get_latest_work_day()})

    result = list(r)
    r = pd.DataFrame(result)
    industry_group = r.groupby(["prev_trend", 'trend'])
    pass
    pass


def run_week():
    now = datetime.now()
    week_start = date_util.get_week_start(now)
    week_end = date_util.get_week_end(now)

    r = db.trade_point.find(
        {"update": {
            "$gt": week_start,
            "$lt": week_end
        }})
    result = list(r)
    df = pd.DataFrame(result)
    group_df = df.groupby(['name'])
    print(r)


def run_another():
    r = db.trade_point.find(
        {"update": datetime(2022, 6, 30, 0, 0, 0)})
    result = list(r)
    df = pd.DataFrame(result)
    group_df = df.groupby(['industry', 'prev_trend', 'trend'])
    a = group_df.size()
    counts = {}
    items = {}
    for keys, group in group_df:
        counts[",".join(keys)] = len(group)
        items[",".join(keys)] = group.to_dict("records")

    sorted(counts.items(), key=lambda d: d[1], reverse=True)

    print(counts)

def get_industry_composition(df):
    """
    获取行业组成
    :return:
    """
    group_df = df.groupby(['industry'])
    df_count = group_df.size().sort_values(ascending=False)
    main = {}
    for k,v in df_count.items():
        main[k] = dict()
    inner_group = df.groupby(['industry', 'prev_trend', 'trend'])
    # 根据行业分组
    for industries,group in inner_group:
        industry = industries[0]
        trends = industries[1]+"-"+industries[2]
        main[industry][trends] = dict(count = len(group),stocks=group[['current_bot_type_slope','current_top_type_slope','name']].to_dict("records"))

    for k in main.keys():
        main[k] = dict(sorted(main[k].items(), key=lambda d: d[1]['count'], reverse=True))
    print(main)
    pass


if __name__ == "__main__":
    # run_another()
    r = db.trade_point.find(
        {"date": {"$lte": datetime(2022, 6, 30, 0, 0, 0)},
         "update": {"$gte": datetime(2022, 6, 30, 0, 0, 0)}}
       )
    result = list(r)
    df = pd.DataFrame(result)
    get_industry_composition(df)
