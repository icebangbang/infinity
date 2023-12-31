from app.main.stock.chart.Line import Line
from app.main.db.mongo import db
from app.main.stock.service import trend_service
from app.main.utils import date_util


class TrendTable(Line):
    """
    趋势列表展示
    """

    def generate(self, **kwargs):
        end_date = kwargs['date']
        end_date = date_util.parse_date_time(end_date)
        trend_info = trend_service.get_trend_info(date_util.get_start_of_day(end_date))

        return dict(
            columns=[
                {"title": '板块名', "dataIndex": 'name', "key": 'name'},
                {"title": '当前差值', "dataIndex": 'currentDiff', "key": 'currentDiff', "useSort": True},
                {"title": '当前上行值', "dataIndex": 'currentUpValue', "key": 'currentUpValue', },
                {"title": '当前下行值', "dataIndex": 'currentDownValue', "key": 'currentDownValue', },
                {"title": '当前放大值', "dataIndex": 'currentEnlargeValue', "key": 'currentEnlargeValue', },
                {"title": '当前收敛值', "dataIndex": 'currentConvergenceValue', "key": 'currentConvergenceValue', },
                {"title": '最低上行值', "dataIndex": 'lowestUpValue', "key": 'lowestUpValue'},
                {"title": '最高上行值', "dataIndex": 'highestUp', "key": 'highestUp'},
                {"title": '最大差值', "dataIndex": 'maxDiffValue', "key": 'maxDiffValue'},
                {"title": '高点对比值', "dataIndex": 'up_slop', "key": 'up_slop'},
                {"title": '低点对比值', "dataIndex": 'down_slop', "key": 'down_slop', "useSort": True},
            ],
            data=trend_info['records'],
            industryInfo=trend_info['industryInfo']
        )
