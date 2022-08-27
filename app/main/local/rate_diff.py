from app.main.db.mongo import db
from app.main.utils import date_util
import pandas as pd

def _analysis(up_df):
    # 最低上行率
    lowest_up = up_df.iloc[[up_df['rate'].idxmin()]]
    # 历史最高上行率
    highest_up = up_df.iloc[[up_df['rate'].idxmin()]]
    # 区间差距最大的一天,和值
    max_diff = up_df.iloc[[up_df['diff'].idxmax()]]
    # 当前区间差距
    current_diff = up_df.iloc[[len(up_df)-1]]

    result = dict(lowestUpValue=float(lowest_up['rate']),
                  lowestUpDay=pd.to_datetime(lowest_up.iloc[0]['date']).to_pydatetime(),
                  highestUp=float(highest_up['rate']),
                  highestUpDay=pd.to_datetime(highest_up.iloc[0]['date']).to_pydatetime(),
                  maxDiffValue=float(max_diff['diff']),
                  maxDiffDay=pd.to_datetime(max_diff.iloc[0]['date']).to_pydatetime(),
                  current_diff=float(current_diff['rate']))
    return result

def get_trend_list():
    config = db['config']
    boards = config.find_one({"name": "board"},{"_id":0})
    industries = boards['value']

    trend_data = db['trend_data']
    end = date_util.get_latest_work_day()
    start = date_util.get_work_day(end, 120)
    trend_data_list = list(trend_data.find({"industry": {"$in": industries},
                                                    "date": {"$gte": start, "$lte": end},
                                                    }))
    total = []
    df = pd.DataFrame(trend_data_list)
    df.sort_values("date", ascending=True,inplace=True)
    for industry in industries:
        up = df[(df['industry']==industry) & (df['trend']=='up')].reset_index(drop=True)
        down = df[(df['industry']==industry) & (df['trend']=='down')].reset_index(drop=True)

        rate_diff = down['rate']-up['rate']
        up['diff'] = rate_diff
        latest = rate_diff[0]
        result = _analysis(up)
        result['name'] = industry
        # total[industry] = round(latest,2)
        total.append(result)
    return total