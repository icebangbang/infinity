# codes = [i for i in range(16)]
# for i in range(0, 16, 5):
#     group = codes[i:i + 5]
#     print(group)
from app.main.db.mongo import db
from app.main.utils import date_util
from datetime import datetime


class TaskInput:
    def __init__(self,kwargs):
        params = kwargs.get("params", {})
        from_date_ts = params.get("from_date_ts", None)
        end_date_ts = params.get("end_date_ts", None)
        global_task_id = params.get("global_task_id", None)

        from_date = date_util.get_start_of_day(date_util.from_timestamp(int(from_date_ts))) \
            if from_date_ts is not None else date_util.get_start_of_day(datetime.now())

        end_date = date_util.get_start_of_day(date_util.from_timestamp(int(end_date_ts))) \
            if end_date_ts is not None else date_util.get_start_of_day(datetime.now())

        self.global_task_id = global_task_id
        self.from_date = from_date
        self.end_date = end_date



if __name__ == "__main__":
    from app.main.stock.service import trend_service
    from app.main.stock.dao import stock_dao

    # stocks = stock_dao.get_all_stock(dict(code=1))
    # codes = [stock['code'] for stock in stocks]
    code_name_map = stock_dao.get_code_name_map()
    #
    # data_list = list(db['stock_detail'].find({"code": {"$in": codes}}))
    #
    # r = list(db['trend_point'].find(
    #     {"date": {"$lte": datetime(2023, 2, 17)}, "update": {"$gte": datetime(2023, 2, 17)}}))
    #
    # codes2 = [r['code'] for r in list(db['stock_detail'].find({}))]
    # codes = [i['code'] for i in r]
    #
    # diff = set(codes2).difference(set(codes))

    db['trend_point'].delete_many({"industry":"电池","name":"先导智能"})

    for code in ['300450']:
        name = code_name_map.get(code)
        print(code)
        for date in date_util.WorkDayIterator(datetime(2022,1,1),datetime(2023,4,7)):
            print(date)
            start_of_day = date_util.get_start_of_day(date)
            features = stock_dao.get_company_feature(code,date)
            trend_service.save_stock_trend_with_features(code,name,features,start_of_day)