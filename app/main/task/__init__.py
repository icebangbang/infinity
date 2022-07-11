# codes = [i for i in range(16)]
# for i in range(0, 16, 5):
#     group = codes[i:i + 5]
#     print(group)

if __name__ == "__main__":
    from app.main.stock.service import trend_service
    from app.main.stock.dao import stock_dao
    from app.main.utils import date_util
    from datetime import datetime

    stocks = stock_dao.get_all_stock(dict(code=1))
    codes = [stock['code'] for stock in stocks]
    code_name_map = stock_dao.get_code_name_map()

    for code in codes:
        name = code_name_map.get(code)
        print(code)
        for date in date_util.WorkDayIterator(datetime(2022,7,6),datetime(2022,7,6)):
            start_of_day = date_util.get_start_of_day(date)
            features = stock_dao.get_company_feature(code,date)
            trend_service.save_stock_trend_with_features(code,name,features,start_of_day)