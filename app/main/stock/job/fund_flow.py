import akshare as ak
import json
# 即时
# 3日排行
# 20日排行
stock_fund_flow_concept_df = ak.stock_fund_flow_concept(symbol="20日排行")
map = stock_fund_flow_concept_df.to_dict("records")

print(json.dumps(map,indent=2,ensure_ascii=False))