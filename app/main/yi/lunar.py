import sxtwl
import datetime
from app.main.yi.constant import *
import json
import os

# lunar = sxtwl.Lunar()

Zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


class Base():
    def __init__(self, now):
        self.now = now

        # 获取当日的日历信息
        current_day = lunar.getDayBySolar(now.year, now.month, now.day)
        # 获取当日的日历信息
        if current_day.qk >= 0:
            qj_start_time = current_day.jqsj.split(":")

            cur_jq_start = datetime.datetime(now.year, now.month, now.day,
                                             int(qj_start_time[0]), int(qj_start_time[1]), int(qj_start_time[2]))

            # 节气当天,但是时间还没到,还是使用原先的节气
            if (now - cur_jq_start).total_seconds() < 0:
                self.current_jq(now - datetime.timedelta(1))
                self.next_jq(now)
        else:
            self.current_jq(now)
            self.next_jq(now)

    def current_jq(self, now):
        date = now
        day = lunar.getDayBySolar(now.year, now.month, now.day)

        if day.qk >= 0:
            self.cur_jq_name = jqmc[day.jqmc]
            self.cur_jq_index = day.jqmc

            qj_start_time = day.jqsj.split(":")
            self.cur_jq_start = datetime.datetime(date.year, date.month, date.day,
                                                  int(qj_start_time[0]), int(qj_start_time[1]), int(qj_start_time[2]))
        else:
            while day.qk < 0:
                the_day_before = date - datetime.timedelta(1)
                day = lunar.getDayBySolar(the_day_before.year, the_day_before.month, the_day_before.day)
                date = the_day_before

            self.cur_jq_name = jqmc[day.jqmc]
            self.cur_jq_index = day.jqmc

            qj_start_time = day.jqsj.split(":")
            self.cur_jq_start = datetime.datetime(date.year, date.month, date.day,
                                                  int(qj_start_time[0]), int(qj_start_time[1]), int(qj_start_time[2]))

    def next_jq(self, now):
        date = now
        day = lunar.getDayBySolar(now.year, now.month, now.day)
        while day.qk < 0:
            the_day_after = date + datetime.timedelta(1)
            day = lunar.getDayBySolar(the_day_after.year, the_day_after.month, the_day_after.day)
            date = the_day_after

        self.next_jq_name = jqmc[day.jqmc]
        self.next_jq_index = day.jqmc

        qj_start_time = day.jqsj.split(":")
        self.next_jq_start = datetime.datetime(date.year, date.month, date.day,
                                               int(qj_start_time[0]), int(qj_start_time[1]), int(qj_start_time[2]))


class Big6ren():
    jq_list = list()

    def prepare(self):
        now = self.now
        lunar_start = datetime.datetime(now.year - 1, 10, 1)
        day = lunar.getDayBySolar(lunar_start.year, lunar_start.month, lunar_start.day)

        date = lunar_start
        while True:
            if day.jqsj != '':
                if day.y > now.year:
                    break
                # if date.year != now.year:
                #     date = date + datetime.timedelta(1)
                #     day = lunar.getDayBySolar(date.year, date.month, date.day)
                #     continue
                qj_start_time = day.jqsj.split(":")
                jq_start = datetime.datetime(day.y, day.m, day.d,
                                             int(qj_start_time[0]), int(qj_start_time[1]),
                                             int(qj_start_time[2]))
                if jqmc[day.jqmc] not in in_use:
                    date = date + datetime.timedelta(1)
                    day = lunar.getDayBySolar(date.year, date.month, date.day)
                    continue
                self.jq_list.append(dict(time=jq_start, jq=jqmc[day.jqmc], jq_index=day.jqmc))
            date = date + datetime.timedelta(1)
            day = lunar.getDayBySolar(date.year, date.month, date.day)
        with open(str(now.year) + ".json", 'w') as f:
            json.dump(self.jq_list, f, cls=DateEncoder, ensure_ascii=False)
        return day

    def __init__(self, now):
        self.now = now
        if os.path.exists(str(now.year) + ".json"):
            with open(str(now.year) + ".json", 'r') as f:
                list = json.load(f)
                for l in list:
                    l['time'] = datetime.datetime.strptime(l['time'], '%Y-%m-%d %H:%M:%S')
                    self.jq_list.append(l)
            day = lunar.getDayBySolar(now.year, now.month, now.day)
        else:
            day = self.prepare()
        # 地支下标
        if 23 <= now.hour < 1:
            self.hour_index = 0
        elif 1 <= now.hour < 3:
            self.hour_index = 1
        elif 3 <= now.hour < 5:
            self.hour_index = 2
        elif 5 <= now.hour < 7:
            self.hour_index = 3
        elif 7 <= now.hour < 9:
            self.hour_index = 4
        elif 9 <= now.hour < 11:
            self.hour_index = 5
        elif 11 <= now.hour < 13:
            self.hour_index = 6
        elif 13 <= now.hour < 15:
            self.hour_index = 7
        elif 15 <= now.hour < 17:
            self.hour_index = 8
        elif 17 <= now.hour < 19:
            self.hour_index = 9
        elif 19 <= now.hour < 21:
            self.hour_index = 10
        elif 21 <= now.hour < 23:
            self.hour_index = 11

        for index, value in enumerate(self.jq_list):
            # 时间还没到的话,还要换成之前的节气
            if (self.now - value['time']).total_seconds() <= 0:
                self.next_jq_name = value['jq']
                self.next_jq_index = value['jq_index']

                self.cur_jq_name = self.jq_list[index - 1]['jq']
                self.cur_jq_index = self.jq_list[index - 1]['jq_index']
                break
        self.day_gan_index = day.Lday2.tg
        self.day_zhi_index = day.Lday2.dz
        self.day_gan = Gan[day.Lday2.tg]
        self.day_zhi = Zhi[day.Lday2.dz]

    def get_section(self):
        for index, value in enumerate(self.jq_list):
            if (self.now - value['time']).total_seconds() <= 0:
                self.next_jq_name = value['jq']
                self.next_jq_index = value['jq_index']

                self.cur_jq_name = self.jq_list[index - 1]['jq']
                self.cur_jq_index = self.jq_list[index - 1]['jq_index']


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


# d = Big6ren(datetime.datetime.now())
# d.prepare()
# print()
if __name__ == "__main__":
    jq_list = []
    now = datetime.datetime.now()
    lunar_start = datetime.datetime(now.year - 1, 10, 1)
    day = sxtwl.fromSolar(lunar_start.year, lunar_start.month, lunar_start.day)

    date = lunar_start
    while True:
        if day.hasJieQi():
            if day.getSolarYear() > now.year:
                break
            # if date.year != now.year:
            #     date = date + datetime.timedelta(1)
            #     day = lunar.getDayBySolar(date.year, date.month, date.day)
            #     continue
            qj_start_time = sxtwl.JD2DD(day.getJieQiJD())
            jq_start = datetime.datetime(day.getSolarYear(), day.getSolarMonth(), day.getSolarDay(),
                                         int(qj_start_time.h), int(qj_start_time.m),
                                         int(qj_start_time.s))
            jq_list.append(dict(time=jq_start, jq=jqmc[day.getJieQi()], jq_index=day.getJieQi))

            # date = date + datetime.timedelta(1)
            # day = sxtwl.fromSolar(date.year, date.month, date.day)
        date = date + datetime.timedelta(1)
        day = sxtwl.fromSolar(date.year, date.month, date.day)
    pass
