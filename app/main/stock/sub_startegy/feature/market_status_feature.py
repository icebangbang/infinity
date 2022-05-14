import logging
from decimal import Decimal

from backtrader.feeds import PandasData

from app.main.stock import constant
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
from app.main.utils import cal_util


class MarketStatusFeature(SubST):
    """
    市场涨跌停情况分析
    """

    def __init__(self, **kwargs):
        pass

    def init_ind(self, data: PandasData, company: Company):
        """
        初始化指标
        :return:
        """
        pass

    def next(self, data: PandasData, company: Company):
        """
        :return:
        """
        day = data.buflen() - len(data)
        if day != 0:
            return  # 只考虑当日触发情况
        try:
            prev_close = data.prev_close.get(ago=0, size=len(data))
            close = data.close.get(ago=0, size=len(data))
            code: str = company.code

            prev_close_reverse = list(prev_close)
            prev_close_reverse.reverse()
            close_reverse = list(close)
            close_reverse.reverse()

            up_limit_str = ""
            for index, close in enumerate(close_reverse):
                close_2 = close
                close_1 = prev_close_reverse[index]
                if close_1 == 0: continue
                # 涨停分析
                if code.startswith("3") or code.startswith("68"):
                    if Decimal(close_1 * 1.2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                            Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                        # 20cm
                        up_limit_str = up_limit_str+"1"
                    else:
                        up_limit_str = up_limit_str + "0"
                    continue

                if "ST" in company.name:
                    if Decimal(close_1 * 1.05).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                            Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                        up_limit_str = up_limit_str+"1"
                    else:
                        up_limit_str = up_limit_str + "0"
                    continue

                if Decimal(close_1 * 1.1).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                        Decimal(close_2).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0:
                    up_limit_str = up_limit_str+"1"
                else:
                    up_limit_str = up_limit_str + "0"
            cont_up_limit_group = up_limit_str.split("0")
            # 连板数获取
            if cont_up_limit_group[0] != '':
                company.set(constant.continuous_up_limit_count,len(cont_up_limit_group[0]))

            up_limit_str_20 = up_limit_str[0:20]
            company.set(constant.up_limit_count_20, up_limit_str_20.count("1"))
        except Exception as e:
            logging.info(e)

if __name__ == "__main__":
    s = "1010111110"
    print(s.count("1"))

