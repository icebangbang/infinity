import logging

from app.main.stock.dao import board_dao, k_line_dao
from datetime import datetime

from app.main.stock.sub_startegy.board_feature.price_in_board_feature import PriceInBoardFeature


def dump_board_feature(date, names:list):
    """
    """
    features_clz_list = [PriceInBoardFeature]
    features = []
    for name in names:
        feature = dict(name=name)
        features.append(feature)
        for features_clz in features_clz_list:
            feature.update(features_clz().run(date,name))

    return features


if __name__ == "__main__":
    base_date = datetime(2019, 1, 2)
    features = dump_board_feature(base_date,['白酒'])
    print(123)
