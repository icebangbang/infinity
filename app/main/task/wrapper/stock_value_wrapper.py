from app.main.stock.dao import stock_dao
from app.main.stock.service import fund_service
from app.main.task.wrapper.sub_task import cpu_task
from app.main.utils import simple_util


class StockValueTask:
    def split(self):
        """
        分割的方法
        :return:
        """
        stocks = stock_dao.get_all_stock(dict(code=1))
        codes = [stock['code'] for stock in stocks]

        step = int(len(codes) / 25)
        for i in range(0, len(codes), step):
            group = codes[i:i + step]
            # 考虑异步提交
            invoke_info = dict(
                path = self.get_clz_path(),
                kwargs = dict(
                    codes = ",".join(group)
                )
            )
            cpu_task.apply_async(args=[invoke_info])

    def invoke(self,codes):
        codes = codes.split(",")
        stocks = stock_dao.get_stock_detail_list(codes)
        fund_service.backtrading_stock_value(stocks)


    def get_clz_path(self):
        return 'app.main.task.wrapper.stock_value_wrapper.StockValueTask'


if __name__ == '__main__':
     p = simple_util.get_method_by_path("app.main.task.wrapper.stock_value_wrapper.StockValueTask")
     print(p.get_clz_path())