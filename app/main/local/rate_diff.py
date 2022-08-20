from app.main.db.mongo import db
from app.main.utils import date_util
import pandas as pd

def analysis(up_df):
    # 最低上行率
    lowest_up = up_df.iloc[[up['rate'].idxmin()]]
    # 历史最高上行率
    highest_up = up_df.iloc[[up['rate'].idxmin()]]
    # 区间差距最大的一天,和值
    min_diff = up_df.iloc[[up['diff'].idxmin()]]
    # 当前区间差距
    current_diff = up_df.iloc[[len(up_df)-1]]
    pass


board_detail = db['board_detail']
boards = board_detail.find({"type": 2})
industries  = [board['board'] for board in boards]

trend_data = db['trend_data']
end = date_util.get_latest_work_day()
start = date_util.get_work_day(end, 60)
trend_data_list = list(trend_data.find({"industry": {"$in": industries},
                                                "date": {"$gte": start, "$lte": end},
                                                }))
total = {}
df = pd.DataFrame(trend_data_list)
df.sort_values("date", ascending=True,inplace=True)
for industry in industries:
    up = df[(df['industry']==industry) & (df['trend']=='up')].reset_index(drop=True)
    down = df[(df['industry']==industry) & (df['trend']=='down')].reset_index(drop=True)

    rate_diff = down['rate']-up['rate']
    up['diff'] = rate_diff
    latest = rate_diff[0]
    analysis(up)
    total[industry] = round(latest,2)
pass
