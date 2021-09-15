from app.main.stock.dao import board_dao
from app.main.stock.job import bt_runner
from datetime import datetime

from app.main.stock.service import board_service, stock_service, stock_index_service
from app.main.stock.sub_startegy.up_sma import UpSma
from app.main.stock.sub_startegy.trend.ma60 import MediumLongTerm

def get_board_status():
    """
    中长期(Medium&LongTerm)指数强弱判断
    """
    from_date = datetime(2021, 3, 1)
    to_date = datetime(2021, 9, 14)
    data = board_service.get_board_k_line(from_date, to_date)
    data = data[data['type']==3]
    data = data.set_index("date", drop=False)

    sub_st = [MediumLongTerm]
    kwargs = {"ma_period": 17,
              "ma_match_num": 17,
              "up_mid_bolling_period": 1}

    company_group = bt_runner.run(from_date, to_date, daily_price=data, key="name", sub_st=sub_st, **kwargs)


    ml_term_up = []
    ml_term_down = []

    for company in company_group.get_companies():
        c1 = company.get("close_gte_ma60", False)
        c2 = company.get("ma60[0]_gte_ma60[-1]", False)
        c3 = company.get("dif>0", False)

        if c1 and c1 and c3:
            ml_term_up.append(company)

        if c1 is False and c2 is False and c3 is False:
            ml_term_down.append(company)

    print([str(company) for company in ml_term_up])
    print([str(company) for company in ml_term_down])

if __name__ == "__main__":
    get_board_status()
