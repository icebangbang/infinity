import logging
from decimal import Decimal

from backtrader.feeds import PandasData

from app.main.stock import constant
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
from app.main.utils import cal_util


class StockStatusFeature(SubST):
    """
    炸板情况分析
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
            prev_close = data.prev_close[0]
            close = data.close[0]
            code: str = company.code
            open = data.open[0]
            high = data.high[0]
            low = data.low[0]

            up_limit_str = ""

            scale = 1.1
            if code.startswith("3") or code.startswith("68"):
                scale = 1.2
            if "ST" in company.name:
                scale = 1.05

            if Decimal(prev_close * scale).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(open).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0 and low==open:
                # 一字板
                company.set(constant.yi_zi_ban, True)

            if Decimal(prev_close * scale).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP").compare(
                    Decimal(high).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")) == 0 and high !=close:
                company.set(constant.kai_ban, True)
        except Exception as e:
            logging.info(e)


if __name__ == "__main__":
    s = "1010111110"
    print(s.count("1"))
