import akshare as ak
import pandas as pd


js_news_df = ak.js_news(timestamp="2021-09-16 17:27:18")

# pd.set_option('display.width', 8000) # 设置字符显示宽度
# pd.set_option('display.max_rows', None) # 设置显示最大行
print(js_news_df)