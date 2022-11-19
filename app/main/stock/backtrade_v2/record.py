class StockTradeRecord:
    """
    股票交易历史
    """

    def __init__(self, type, deal_num, deal_price, trade_time, motivation):
        """

        :param type: 成交类型,1买入,-1卖出
        :param deal_num: 成交数
        :param deal_price:  成交价格
        :param trade_time: 成交时间
        :param motivation: 成交动机
        """
        self.type = type
        self.deal_num = deal_num
        self.deal_price = deal_price
        self.trade_time = trade_time
        self.motivation = motivation


class StockRefreshRecord:

    def __init__(self, cost, price, date):
        self.cost = cost
        self.price = price
        self.date = date
