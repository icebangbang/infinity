from backtrader.feeds import PandasData

from app.main.stock import constant
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST


def custom_sort(e):
    return e['v']


class BoxBoundary(SubST):
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

        :return:
        """
        day = data.buflen() - len(data)
        if day != 0: return  # 从当日开始统计数据

        periods = [5, 10, 20, 30, 40, 50, 60, 90, 200]
        box = {"close": data.close[0]}

        for period in periods:
            high = list(data.high.get(ago=-1, size=period))
            if len(high) < period: continue

            high.sort(reverse=True)

            low = list(data.low.get(ago=-1, size=period))
            low.sort(reverse=False)

            box["D" + str(period)] = dict(
                top=high[0],
                bottom=low[0]
            )

        company.set(constant.box_boundary, box)
