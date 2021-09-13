import akshare as ak
import json
# 即时
# 3日排行
# 20日排行
def flow():
    stock_fund_flow_concept_df = ak.stock_fund_flow_concept(symbol="即时2")
    map = stock_fund_flow_concept_df.to_dict("records")

    print(json.dumps(map,indent=2,ensure_ascii=False))


def board_flow():
    stock_sector_fund_flow_rank_df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流")
    print(stock_sector_fund_flow_rank_df)