from app.main.stock.dao import board_dao, k_line_dao, stock_dao
from app.main.stock.job import bt_runner
from datetime import datetime
import pandas as pd

from app.main.stock.service import board_service, stock_service, stock_index_service
from app.main.stock.sub_startegy.up_sma import UpSma
from app.main.stock.sub_startegy.trend.term import MediumLongTerm, MediumShortUpTerm
from app.main.stock.sub_startegy.trend.medium_short_up_trend import MediumShortUpTrend


def get_stock_status():
    """
    中长期(Medium&LongTerm)指数强弱判断
    """
    from_date = datetime(2021, 3, 1)
    to_date = datetime(2021, 9, 16)
    data = pd.DataFrame(k_line_dao.get_k_line_by_code(["300005"],from_date, to_date))
    # data = pd.DataFrame(k_line_dao.get_k_line_data(from_date, to_date))
    data = data.set_index("date", drop=False)

    sub_st = [MediumShortUpTrend, ]
    kwargs = {"ma_period": 17,
              "ma_match_num": 17,
              "up_mid_bolling_period": 1,
              "timeline_limit": 30}

    company_group = bt_runner.run(from_date, to_date, daily_price=data, key="code", sub_st=sub_st, **kwargs)

    ml_term_up = []

    for company in company_group.get_companies():
        # c1 = company.get("close_gte_ma20")
        # c2 = company.get("ma20[0]_gte_ma20[-1]")
        # c3 = company.get("dif>0")
        # c4 = company.get("dif[-1]<0")

        c1 = company.get("close_gte_ma20")
        c2 = company.get("ma20[0]_gte_ma20[-1]")
        c3 = company.get("macd_incr")
        c4 = company.get("kdj_golden")

        if c1 and c2 and c3 and c4:
            ml_term_up.append(company)

    codes = [str(company) for company in ml_term_up]
    print([str(company) for company in ml_term_up])

    return codes


if __name__ == "__main__":
    codes = get_stock_status()
    # codes = ['600058', '600167', '600222', '600227', '600243', '600257', '600299', '600308', '600319', '600354', '600358', '600371', '600406', '600455', '600530', '600540', '600583', '600613', '600678', '600803', '600819', '600956', '600977', '601579', '603079', '603080', '603090', '603168', '603269', '603626', '603696', '603789', '603822', '603838', '603959', '603970', '603983', '603987', '000523', '000529', '000669', '000713', '000798', '000803', '000876', '000990', '000998', '002031', '002100', '002112', '002124', '002237', '002261', '002267', '002290', '002304', '002309', '002321', '002330', '002655', '002665', '002722', '002746', '002779', '002783', '002865', '003003', '300071', '300094', '300119', '300168', '300169', '300179', '300243', '300268', '300288', '300402', '300422', '300423', '300468', '300503', '300511', '300620', '300659', '300830', '300849', '300865', '300886', '300937']
    stock_details = stock_dao.get_stock_detail_list(codes)
    stock_map ={}
    boards = []
    for stock in stock_details:
        stock['code'] = stock
        boards.extend(stock['board'])

    pd.DataFrame(boards).groupby(0).apply(lambda x:x.sort_values(0,ascending=False))

    # pd.DataFrame(boards)[0].value_counts(normalize=False, sort=True).to_frame('count').reset_index()
    if len(codes) !=0:
        stock_service.publish(10, 30, codes, stock_map)


