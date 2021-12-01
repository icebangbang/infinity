import akshare as ak
from app.main.db.mongo import db
from app.main.utils import date_util


def sync_ppi():
    data_list = ak.chinese_ppi()

    data_format = []

    for data in data_list:
        array = data.split(",")
        date = date_util.parse_date_time(array[0], "%Y-%m-%d")
        current = array[1]  # 当前
        grace = array[2]  # 增长
        accum = array[3]  # 累计

        data_format.append(dict(date=date, current=current, grace=grace, accum=accum))

    set = db['ppi']
    set.drop()
    set.insert_many(data_format)


def sync_cpi():
    data_list = ak.chinese_cpi()

    data_format = []

    for data in data_list:
        array = data.split(",")
        date = date_util.parse_date_time(array[0], "%Y-%m-%d")
        country_current = array[1]  # 当前
        country_grace_tb = array[2]  #
        country_grace_hb = array[3]  #
        country_accum = array[4]

        city_current = array[5]  # 当前
        city_grace_tb = array[6]  #
        city_grace_hb = array[7]  #
        city_accum = array[8]

        village_current = array[9]  # 当前
        village_grace_tb = array[10]  #
        village_grace_hb = array[11]  #
        village_accum = array[12]

        data_format.append(dict(date=date,
                                country_current=country_current, country_grace_tb=country_grace_tb,
                                country_grace_hb=country_grace_hb, country_accum=country_accum,
                                city_current=city_current, city_grace_tb=city_grace_tb, city_grace_hb=city_grace_hb,
                                city_accum=city_accum,
                                village_current=village_current,
                                village_grace_tb=village_grace_tb,
                                village_grace_hb=village_grace_hb,
                                village_accum=village_accum
                                ))

    set = db['cpi']
    set.drop()
    set.insert_many(data_format)

def sync_pig_data():
    pig_data = ak.pig_data()
    set = db['pig_data']
    set.drop()
    set.insert_many(pig_data)

if __name__ == "__main__":
    # sync_cpi()
    # sync_ppi()
    sync_pig_data()
