from app.main.stock.service import trade_service
from app.main.utils import object_util

# 同步个股日k线
# 个股特征跑批-个股趋势跑批-板块趋势和成交额聚合-

TRADE_MAPPING = {
    "持仓查询":trade_service.position_query,
}

if __name__  == "__main__":
    r = object_util.get_method(trade_service)
    print(123)