"""
排盘专用类
"""
import sxtwl

from app.main.model.yi.ganzhi import BaZi
from app.main.yi.constant import Gan, Zhi
from datetime import datetime


def get_pan(date)->BaZi:
    day = sxtwl.fromSolar(date.year, date.month, date.day)
    year_gz_index = day.getYearGZ()

    year_gz_str = Gan[year_gz_index.tg] + Zhi[year_gz_index.dz]
    # 月干支
    month_gz_index = day.getMonthGZ()
    month_gz_str = Gan[month_gz_index.tg] + Zhi[month_gz_index.dz]

    # 日干支
    day_gz_index = day.getDayGZ()
    day_gz_str = Gan[day_gz_index.tg] + Zhi[day_gz_index.dz]

    # 时干支
    # 第一个参数为该天的天干，第二个参数为小时
    hour_gz_index = sxtwl.getShiGz(year_gz_index.tg, date.hour)
    hour_gz_str = Gan[hour_gz_index.tg] + Zhi[hour_gz_index.dz]

    bazi = BaZi(
        year_gan=Gan[year_gz_index.tg],
        year_zhi=Zhi[year_gz_index.dz],
        month_gan=Gan[month_gz_index.tg],
        month_zhi=Zhi[month_gz_index.dz],
        day_gan=Gan[day_gz_index.tg],
        day_zhi=Zhi[day_gz_index.dz],
        hour_gan=Gan[hour_gz_index.tg],
        hour_zhi=Zhi[hour_gz_index.dz],
        year_gan_index=year_gz_index.tg,
        year_zhi_index=year_gz_index.dz,
        month_gan_index=month_gz_index.tg,
        month_zhi_index=month_gz_index.dz,
        day_gan_index=day_gz_index.tg,
        day_zhi_index=day_gz_index.dz,
        hour_gan_index=hour_gz_index.tg,
        hour_zhi_index=hour_gz_index.dz
    )

    return bazi


if __name__ == "__main__":
    a = get_pan(datetime.now())

    pass
