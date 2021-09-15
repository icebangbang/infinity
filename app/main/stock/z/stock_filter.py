from app.main.stock.dao import board_dao, k_line_dao, stock_dao
from app.main.stock.job import bt_runner
from datetime import datetime
import pandas as pd

from app.main.stock.service import board_service, stock_service, stock_index_service
from app.main.stock.sub_startegy.up_sma import UpSma
from app.main.stock.sub_startegy.trend.ma60 import MediumLongTerm, MediumShortTerm


def get_stock_status():
    """
    中长期(Medium&LongTerm)指数强弱判断
    """
    from_date = datetime(2021, 6, 1)
    to_date = datetime(2021, 9, 14)
    # data = pd.DataFrame(k_line_dao.get_k_line_by_code(["000586"],from_date, to_date))
    data = pd.DataFrame(k_line_dao.get_k_line_data(from_date, to_date))
    data = data.set_index("date", drop=False)

    sub_st = [MediumShortTerm, ]
    kwargs = {"ma_period": 17,
              "ma_match_num": 17,
              "up_mid_bolling_period": 1,
              "timeline_limit": 60}

    company_group = bt_runner.run(from_date, to_date, daily_price=data, key="code", sub_st=sub_st, **kwargs)

    ml_term_up = []
    ml_term_down = []

    for company in company_group.get_companies():
        c1 = company.get("close_gte_ma20")
        c2 = company.get("ma20[0]_gte_ma20[-1]")
        c3 = company.get("dif>0")
        c4 = company.get("dif[-1]<0")

        if c1 and c1 and c3 and c4:
            ml_term_up.append(company)

        if c1 is False and c2 is False and c3 is False:
            ml_term_down.append(company)

    codes = [str(company) for company in ml_term_up]
    stock_dao.get_stock_detail_list(codes)
    # print([str(company) for company in ml_term_down])


if __name__ == "__main__":
    # get_stock_status()
    codes = ['600346', '600499', '600770', '603222', '603326', '603353', '603520', '603636', '603665', '603867',
             '603896', '603958', '603960', '688037', '688559', '000572', '000586', '000851', '002261', '002455',
             '002625', '002647', '002702', '002703', '002715', '002821', '300088', '300183', '300194', '300225',
             '300312', '300323', '300326', '300363', '300378', '300451', '300557', '300768']
    stock_details = stock_dao.get_stock_detail_list(codes)
    stock_map = {stock['code']: stock for stock in stock_details}
    stock_service.publish(10, 30, codes, stock_map)
