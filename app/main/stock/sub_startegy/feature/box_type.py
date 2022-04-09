from backtrader.feeds import PandasData

from app.main.stock import constant
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
from app.main.utils import cal_util


def custom_sort(e):
    return e['v']


class BoxType(SubST):

    def get_reverse_point(self, points):
        """
        三点确定中间点的斜率情况
        获取反转点
        :param point:
        :return: pos_p  先下后上
                 neg_p  先上后下
        """
        pos_p = []
        neg_p = []
        total_p = []
        point_index = []

        for i, point in enumerate(points):
            if i == 0 or i == len(points) - 1: continue
            prev, useless = cal_util.get_line([points[i - 1]['value'], points[i]['value']])
            next, useless = cal_util.get_line([points[i]['value'], points[i + 1]['value']])
            if prev >= 0 and next < 0:
                neg_p.append(i)
                total_p.append(i)
                point_index.append(point['index'])
            if prev < 0 and next >= 0:
                pos_p.append(i)
                total_p.append(i)
                point_index.append(point['index'])

        return pos_p, neg_p, total_p, point_index

    """
    k线趋势判断辅助变量
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
                results.append(dict(index=i, value=item))
                continue
            target = item
            pre = arrays[i - 1]
            next = arrays[i + 1]

            if target > pre and target > next:
                # results.append(dict(i=i, v=item))
                results.append(dict(index=i, value=item))
        return results

    def get_bottom_type(self, arrays) -> list:
        """
        筛选底分型
        :param arrays:
        :return:
        """
        results = []

        for i, item in enumerate(arrays):
            if i == 0 or i == len(arrays) - 1:
                # results.append(dict(i=i, v=item))
                results.append(dict(index=i, value=item))
                continue
            target = item
            pre = arrays[i - 1]
            next = arrays[i + 1]

            if target < pre and target < next:
                # results.append(dict(i=i, v=item))
                results.append(dict(index=i, value=item))

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

        high = data.high.get(ago=0, size=len(data))
        high_type_list: list = self.get_top_type(high)
        pos_p, neg_p, total_p, point_index = self.get_reverse_point(high_type_list)
        # point_dt_index = [data.datetime.datetime(i - len(high)) for i in point_index]
        # 当前趋势范围点
        current_trend_scope = high_type_list[total_p[-1]:]
        # 最近趋势范围点
        prev_trend_scope = high_type_list[total_p[-2]:total_p[-1] + 1]

        inflection_point = current_trend_scope[0]
        inf_h_point_date = data.datetime.datetime(inflection_point['index'] - len(high) + 1)
        current_top_type_slope, c = cal_util.get_line([i['value'] for i in current_trend_scope])
        prev_top_type_slope, c = cal_util.get_line([i['value'] for i in prev_trend_scope])

        company.set(constant.current_top_trend_size, current_trend_scope[-1]['index'] - current_trend_scope[0]['index'])
        company.set(constant.prev_top_trend_size, prev_trend_scope[-1]['index'] - prev_trend_scope[0]['index'])

        low = data.low.get(ago=0, size=len(data))
        low_type_list: list = self.get_bottom_type(low)
        pos_p, neg_p, total_p, point_index = self.get_reverse_point(low_type_list)

        # 当前趋势范围点
        current_trend_scope = low_type_list[total_p[-1]:]
        # 最近趋势范围点
        prev_trend_scope = low_type_list[total_p[-2]:total_p[-1] + 1]

        inflection_point = current_trend_scope[0]
        inf_l_point_date = data.datetime.datetime(inflection_point['index'] - len(low) + 1)
        current_bot_type_slope, c = cal_util.get_line([i['value'] for i in current_trend_scope])
        prev_bot_type_slope, c = cal_util.get_line([i['value'] for i in prev_trend_scope])

        company.set(constant.current_top_type_slope, current_top_type_slope)
        company.set(constant.current_bot_type_slope, current_bot_type_slope)
        company.set(constant.prev_top_type_slope, prev_top_type_slope)
        company.set(constant.prev_bot_type_slope, prev_bot_type_slope)

        company.set(constant.current_bot_trend_size, current_trend_scope[-1]['index'] - current_trend_scope[0]['index'])
        company.set(constant.prev_bot_trend_size, prev_trend_scope[-1]['index'] - prev_trend_scope[0]['index'])

        company.set(constant.inf_h_point_date, inf_h_point_date)
        company.set(constant.inf_l_point_date, inf_l_point_date)
        # company.set(constant.box_top_formulas, dict(k=tm, c=tc))
        # company.set(constant.box_bottom_formulas, dict(k=bm, c=bc))
