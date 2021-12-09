from app.main.db.mongo import db
from datetime import datetime
from typing import List
import pandas as pd
import akshare as ak


def get_oldest_k_line(code, level='day'):
    db_name = "k_line_" + level
    my_set = db[db_name]

    return list(my_set.find({"code": code}).sort("date", -1).limit(1))


def get_concept_oldest_k_line(name):
    db_name = "board_k_line"
    my_set = db[db_name]

    return list(my_set.find({"name": name}).sort("_id", -1).limit(1))


def dump_k_line(data, level='day'):
    """
    存储个股日k
    :param data:
    :param level:
    :return:
    """
    db_name = "k_line_" + level
    my_set = db[db_name]

    if len(data) == 0:
        return

    return my_set.insert(data)


def update_k_line(code, data):
    db_name = "k_line_day"
    my_set = db[db_name]

    for d in data:
        r = my_set.update({"code": code, "date": d['date']}, d, upsert=True)


def clear_k_line(level='week'):
    db_name = "k_line_" + level
    my_set = db[db_name]
    my_set.delete_many({})


def dump_board_k_line(data, level='day'):
    db_name = "board_k_line"
    my_set = db[db_name]

    if len(data) == 0:
        return

    return my_set.insert(data)


def update_board_k_line(name, date, data):
    db_name = "board_k_line"
    my_set = db[db_name]

    for d in data:
        r = my_set.update({"name": name, "date": d['date']}, d, upsert=True)


def get_k_line_by_code(code: List,
                       start_day: datetime,
                       end_day: datetime,
                       level='day'):
    """
    获取特定时间和代码的股票走势
    :param code:
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    db_name = "k_line_" + level
    my_set = db[db_name]

    query = my_set.find({"code": {"$in": code},
                         "date": {"$lte": end_day, "$gte": start_day}}) \
        .sort("date", 1)
    return list(query)


def get_k_line_data(
        start_day: datetime,
        end_day: datetime,
        level='day', codes=None) -> List:
    """
    获取特定时间的股票走势
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    db_name = "k_line_" + level
    my_set = db[db_name]
    query_set = {"date": {"$gte": start_day, "$lte": end_day}}
    if codes is not None:
        query_set['code'] = {"$in": codes}

    query = my_set \
        .find(query_set) \
        .sort("date", 1)
    return list(query)


def get_index_kline_data(
        start_day: datetime,
        end_day: datetime,
        level='day') -> List:
    """
    获取特定时间的股票走势
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    db_name = "stock_index_k_line_" + level
    my_set = db[db_name]

    query = my_set \
        .find({"date": {"$lte": end_day, "$gte": start_day}}) \
        .sort("date", 1)
    return list(query)


def get_board_k_line_data(
        name,
        start_day: datetime,
        end_day: datetime,
) -> List:
    """
    获取特定时间的股票走势
    :param start_day:
    :param end_day:
    :param level:
    :return:
    """
    data = \
        ak.stock_board_concept_hist_em(
            symbol=name,
            beg=start_day,
            end=end_day)
    data = pd.DataFrame(data[['日期', '开盘', '收盘', '最高', '最低', '成交量']])
    data.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
    data['name'] = str(name)
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
    data['create_time'] = datetime.now()
    return data


if __name__ == "__main__":
    r = get_k_line_data(datetime(2021, 7, 28), datetime(2021, 8, 28),
                        codes=['300864', '300865', '300866', '300867', '300868', '300869', '300870', '300871', '300872',
                               '300873', '300875', '300876', '300877', '300878', '300879', '300880', '300881', '300882',
                               '300883', '300884', '300885', '300886', '300887', '300888', '300889', '300890', '300891',
                               '300892', '300893', '300894', '300895', '300896', '300897', '300898', '300899', '300900',
                               '300901', '300902', '300903', '300905', '300906', '300907', '300908', '300909', '300910',
                               '300911', '300912', '300913', '300915', '300916', '300917', '300918', '300919', '300920',
                               '300921', '300922', '300923', '300925', '300926', '300927', '300928', '300929', '300930',
                               '300931', '300932', '300933', '300935', '300936', '300937', '300938', '300939', '300940',
                               '300941', '300942', '300943', '300945', '300946', '300947', '300948', '300949', '300950',
                               '300951', '300952', '300953', '300955', '300956', '300957', '300958', '300959', '300960',
                               '300961', '300962', '300963', '300964', '300965', '300966', '300967', '300968', '300969',
                               '300970', '300971', '300972', '300973', '300975', '300976', '300977', '300978', '300979',
                               '300980', '300981', '300982', '300983', '300984', '300985'])
    print(r)
