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
                {"title": '当前差值', "dataIndex": 'currentDiff', "key": 'currentDiff', },
                {"title": '当前上行值', "dataIndex": 'currentUpValue', "key": 'currentUpValue', },
                {"title": '当前下行值', "dataIndex": 'currentDownValue', "key": 'currentDownValue', },
                {"title": '最低上行值', "dataIndex": 'lowestUpValue', "key": 'lowestUpValue'},
                {"title": '最高上行值', "dataIndex": 'highestUp', "key": 'highestUp'},
                {"title": '最低上行值日期', "dataIndex": 'lowestUpDay', "key": 'lowestUpDay'},
                {"title": '最高上行值日期', "dataIndex": 'highestUpDay', "key": 'highestUpDay'},
                {"title": '最大差值', "dataIndex": 'maxDiffValue', "key": 'maxDiffValue'},
                {"title": '最大差值日期', "dataIndex": 'maxDiffDay', "key": 'maxDiffDay'},
                {"title": '高点对比值', "dataIndex": 'up', "key": 'up'},
                {"title": '低点对比值', "dataIndex": 'down', "key": 'down'},
            ],
            data=trend_info['records'],
            industryInfo=trend_info['industryInfo']
        )
