from functools import cmp_to_key

from backtrader.feeds import PandasData

from app.main.stock import constant
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
import backtrader as bt
from typing import List
from app.main.stock.algo import cal


def custom_sort(e):
    return e['v']


class BoxType(SubST):
    """
    箱体判断策略
    """

    def get_top_type(self, arrays) -> list:
        """
        筛选顶分型
        :return:
        """
        results = []

        for i, item in enumerate(arrays):
            if i == 0 or i == len(arrays) - 1:
                # results.append(dict(i=i, v=item))
                results.append(item)
                continue
            target = item
            pre = arrays[i - 1]
            next = arrays[i + 1]

            if target > pre and target > next:
                # results.append(dict(i=i, v=item))
                results.append(item)
        return results

    def get_bottom_type(self, arrays) -> list:
        results = []

        for i, item in enumerate(arrays):
            if i == 0 or i == len(arrays) - 1:
                # results.append(dict(i=i, v=item))
                results.append(item)
                continue
            target = item
            pre = arrays[i - 1]
            next = arrays[i + 1]

            if target < pre and target < next:
                # results.append(dict(i=i, v=item))
                results.append(item)

        return results

    def __init__(self, **kwargs):
        """
        对象初始化
        """
        pass

    def init_ind(self, data: PandasData, company: Company):
        """
        初始化指标
        :return:
        """
        pass

    def next(self, data: PandasData, company: Company):
        """
        n日线策略进行筛选
        :return:
        """
        day = data.buflen() - len(data)
        if day != 0: return  # 从当日开始统计数据

        high = data.high.get(ago=-1, size=20)
        high_type: list = self.get_top_type(high)
        tm, tc, ty, tx = cal.get_top_line(high_type)
        # high_type.sort(reverse=True)

        low = data.low.get(ago=-1, size=20)
        low_type: list = self.get_bottom_type(low)
        bm, bc, by, bx = cal.get_bot_line(low_type)
        # low_type.sort(key=custom_sort)
        # low_type.sort(reverse=False)

        company.set(constant.box_top_formulas, dict(k=tm, c=tc))
        company.set(constant.box_bottom_formulas, dict(k=bm, c=bc))

