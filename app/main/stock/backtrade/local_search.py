from app.main.db.mongo import db
from app.main.utils import date_util
from datetime import datetime
import pandas as pd

stocks = list(db.stock_detail.find({"board":{"$in":["光伏设备"]}}))

codes = [ stock['code'] for stock in stocks]
name_dict = {stock['code']: stock['name'] for stock in stocks}
stocks_features = list(db.stock_feature.find({"date":date_util.get_start_of_day(datetime(2022,5,13)),
                       "code":{"$in":codes}}))

f_dict = [dict(code=name_dict.get(stock['code']),up_median=stock['features']['up_median'],money_median=stock['features']['money_median']) for stock in stocks_features]
df = pd.DataFrame(f_dict)

df.sort_values(by=['up_median', 'up_median'], inplace=True, ascending=False)
pass