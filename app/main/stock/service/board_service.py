import pandas as pd

from app.main.stock.dao import k_line_dao,board_dao


def get_concept_k_line(from_date, to_date, concept_names=None):
    daily_price = None
    if concept_names is None:
        daily_price = pd.DataFrame(board_dao.get_board_k_line_data_from_db(from_date, to_date))
    else:
        # todo 按板块筛选
        pass

    daily_price = daily_price.set_index("date", drop=False)
    return daily_price
