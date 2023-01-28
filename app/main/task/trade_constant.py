from app.main.stock.service import trade_service

# 同步个股日k线
# 个股特征跑批-个股趋势跑批-板块趋势和成交额聚合-

TRADE_MAPPING = {
    "持仓查询":trade_service.position_query,
}