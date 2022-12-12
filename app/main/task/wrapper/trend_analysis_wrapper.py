from app.main.stock.dao import stock_dao, board_dao
from app.main.stock.service import fund_service, trend_analysis_service
from app.main.task.wrapper.sub_task import cpu_task
from app.main.utils import simple_util
from datetime import datetime


class TrendAnalysisTask:
    def split(self):
        """
        分割的方法
        :return:
        """
        boards = board_dao.get_mixed_board()

        step = 1
        for i in range(0, len(boards), step):
            group = boards[i:i + step]
            # 考虑异步提交
            invoke_info = dict(
                path = self.get_clz_path(),
                kwargs = dict(
                    codes = ",".join(group)
                )
            )
            cpu_task.apply_async(args=[invoke_info])

    def invoke(self,boards):
        base_start = 2019
        boards = boards.split(",")
        current_year = datetime.now().year
        year_list = [year for year in range(base_start,current_year)]

        for board in boards:
            for year in year_list:
                trend_analysis_service.find_stocks_by_year(board,year)


    def get_clz_path(self):
        return 'app.main.task.wrapper.trend_analysis_wrapper.TrendAnalysisTask'


if __name__ == '__main__':
     p = simple_util.get_method_by_path("app.main.task.wrapper.stock_value_wrapper.StockValueTask")
     print(p.get_clz_path())