from datetime import datetime, timedelta
from decimal import Decimal
from app.main.stock.dao import k_line_dao, stock_dao
from app.main.utils import date_util
import numpy

if __name__ == "__main__":
    now = datetime.now()
    now = date_util.get_start_of_day(now)
    stocks = stock_dao.get_all_stock(dict(code=1, name=1, _id=0))
    st_stock = {stock['code']: stock['name'] for stock in stocks if "ST" in stock['name']}
    start = date_util.get_work_day(now, 1)
    trade_data_list = k_line_dao.get_k_line_data(start, end)
    groups = {}
    for trade_data in trade_data_list:
        code = trade_data['code']
        items = groups.get(code)
        if items is None:
            items = []
        items.append(trade_data)
        groups[code] = items
    rate_list = []

    up_down_distribution = {"跌停": 0, "跌停~8%": 0, "-8%~-6%": 0, "-6%~-4%": 0, "-4%~-2%": 0, "-2%~0%": 0,
                            "0%~2%": 0, "2%~4%": 0,
                            "4%~6%": 0, "6%~8%": 0, "8%~涨停": 0, "涨停": 0}
    for key, trade_data_list in groups.items():
        if len(trade_data_list) < 2: continue
        close_1 = trade_data_list[0]['close']
        close_2 = trade_data_list[1]['close']
        rate = Decimal((close_2 - close_1) / close_1 * 100).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
        rate_list.append(rate)

        if key.startswith("3") or key.startswith("688"):
            if Decimal(close_1 * 1.2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                # 20cm
                up_down_distribution['涨停'] = up_down_distribution['涨停'] + 1
                continue
        else:
            if key in st_stock.keys() and Decimal(close_1 * 1.05).quantize(Decimal("0.01"),
                                                                           rounding="ROUND_HALF_UP").compare(
                Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                up_down_distribution['涨停'] = up_down_distribution['涨停'] + 1
                continue
            elif Decimal(close_1 * 1.1).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                up_down_distribution['涨停'] = up_down_distribution['涨停'] + 1
                continue

        if key.startswith("3") or key.startswith("688"):
            if Decimal(close_1 * 0.8).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                # 20cm
                up_down_distribution['跌停'] = up_down_distribution['跌停'] + 1
                continue
        else:
            if key in st_stock.keys() and Decimal(close_1 * 0.95).quantize(Decimal("0.01"),
                                                                           rounding="ROUND_HALF_UP").compare(
                Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                up_down_distribution['跌停'] = up_down_distribution['跌停'] + 1
                continue
            elif Decimal(close_1 * 0.9).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                up_down_distribution['跌停'] = up_down_distribution['跌停'] + 1
                continue

        # "跌停~8%": 0, "-8%~-6%": 0, "-6%~-4%": 0, "-4%~-2%": 0, "-2%~0%": 0,
        #                             "0%~2%": 0, "2%~4%": 0,
        #                             "4%~6%": 0, "6%~8%": 0, "8%~涨停": 0, "涨停": 0

        if rate < -8:
            up_down_distribution['跌停~8%'] = up_down_distribution['跌停~8%'] + 1
            continue
        if -8 <= rate < -6:
            up_down_distribution['-8%~-6%'] = up_down_distribution['-8%~-6%'] + 1
            continue
        if -6 <= rate < -4:
            up_down_distribution['-6%~-4%'] = up_down_distribution['-6%~-4%'] + 1
            continue
        if -4 <= rate < -2:
            up_down_distribution['-4%~-2%'] = up_down_distribution['-4%~-2%'] + 1
            continue
        if -2 <= rate < 0:
            up_down_distribution['-2%~0%'] = up_down_distribution['-2%~0%'] + 1
            continue
        if 0 <= rate < 2:
            up_down_distribution['0%~2%'] = up_down_distribution['0%~2%'] + 1
            continue
        if 2 <= rate < 4:
            up_down_distribution['2%~4%'] = up_down_distribution['2%~4%'] + 1
            continue
        if 4 <= rate < 6:
            up_down_distribution['4%~6%'] = up_down_distribution['4%~6%'] + 1
            continue
        if 6 <= rate < 8:
            up_down_distribution['6%~8%'] = up_down_distribution['6%~8%'] + 1
            continue
        if rate >= 8:
            up_down_distribution['8%~涨停'] = up_down_distribution['8%~涨停'] + 1
            continue

    median = numpy.median(rate_list)
    print()
