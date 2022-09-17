from backtrader.feeds import PandasData

from app.main.stock import constant
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST
from app.main.utils import cal_util


def custom_sort(e):
    return e['v']


class BoxType(SubST):



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
        high_type_list: list = cal_util.get_top_type(high)
        pos_p, neg_p, total_p, point_index = cal_util.get_reverse_point(high_type_list)
        # point_dt_index = [data.datetime.datetime(i - len(high)) for i in point_index]
        if len(total_p) == 0:
            current_top_type_slope, c = cal_util.get_line([i['value'] for i in high_type_list])
            company.set(constant.current_top_type_slope, current_top_type_slope)
            company.set(constant.prev_top_type_slope, None)
            company.set(constant.current_top_trend_size, high_type_list[-1]['index'] - high_type_list[0]['index'])
            company.set(constant.prev_top_trend_size, 0)
            company.set(constant.inf_h_point_date, None)
            company.set(constant.inf_h_point_value, None)
        else:
            # 当前趋势范围点
            current_trend_scope = high_type_list[total_p[-1]:]
            # 最近趋势范围点
            if len(total_p) >1:
                prev_trend_scope = high_type_list[total_p[-2]:total_p[-1] + 1]
            else:
                prev_trend_scope = high_type_list[:total_p[-1] + 1]
            prev_top_type_slope, c = cal_util.get_line([i['value'] for i in prev_trend_scope])
            # 当前顶分型趋势的最大一个点的值
            current_max_high_type = max([i['value'] for i in current_trend_scope[0:-1]])

            t = data.datetime.date(0).strftime("%Y-%m-%d")
            print(t)
            inflection_point = current_trend_scope[0]
            inf_h_point_date = data.datetime.datetime(inflection_point['index'] - len(high) + 1)
            current_top_type_slope, c = cal_util.get_line([i['value'] for i in current_trend_scope])

            company.set(constant.current_top_type_slope,current_top_type_slope)
            company.set(constant.prev_top_type_slope, prev_top_type_slope)
            company.set(constant.current_top_trend_size,
                        len(high)-1 - current_trend_scope[0]['index'])
            company.set(constant.inf_h_point_date, inf_h_point_date)
            company.set(constant.inf_h_point_value, inflection_point['value'])
            company.set(constant.inf_h_point_value, inflection_point['value'])
            company.set(constant.current_max_high_type, current_max_high_type)

        low = data.low.get(ago=0, size=len(data))
        low_type_list: list = cal_util.get_bottom_type(low)
        pos_p, neg_p, total_p, point_index = cal_util.get_reverse_point(low_type_list)
        if len(total_p) == 0:
            current_bot_type_slope, c = cal_util.get_line([i['value'] for i in low_type_list])
            company.set(constant.prev_bot_type_slope, None)
            company.set(constant.current_bot_type_slope, current_bot_type_slope)
            company.set(constant.prev_bot_trend_size, 0)
            company.set(constant.current_bot_trend_size, low_type_list[-1]['index'] - low_type_list[0]['index'])
            company.set(constant.inf_l_point_date, None)
            company.set(constant.inf_l_point_value, None)
        else:
            # 当前趋势范围点
            current_trend_scope = low_type_list[total_p[-1]:]
            # 最近趋势范围点
            if len(total_p) > 1:
                prev_trend_scope = low_type_list[total_p[-2]:total_p[-1] + 1]
            else:
                prev_trend_scope = low_type_list[:total_p[-1] + 1]

            inflection_point = current_trend_scope[0]
            inf_l_point_date = data.datetime.datetime(inflection_point['index'] - len(low) + 1)
            current_bot_type_slope, c = cal_util.get_line([i['value'] for i in current_trend_scope])
            prev_bot_type_slope, c = cal_util.get_line([i['value'] for i in prev_trend_scope])

            company.set(constant.current_bot_type_slope, current_bot_type_slope)
            company.set(constant.prev_bot_type_slope, prev_bot_type_slope)

            company.set(constant.current_bot_trend_size,
                        current_trend_scope[-1]['index'] - current_trend_scope[0]['index'])
            company.set(constant.prev_bot_trend_size, len(low)-1 - prev_trend_scope[0]['index'])

            company.set(constant.inf_l_point_date, inf_l_point_date)
            company.set(constant.inf_l_point_value, inflection_point['value'])
        # company.set(constant.box_top_formulas, dict(k=tm, c=tc))
        # company.set(constant.box_bottom_formulas, dict(k=bm, c=bc))
