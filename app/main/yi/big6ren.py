# 大六壬模型
from app.main.yi.lunar import Big6ren
from app.main.yi import constant
import datetime

# 初始化当天的节气信息
lunar = Big6ren(datetime.datetime.now())

# 初始化地支信息,即为大六壬中的地盘,万载不变
dp = constant.Zhi
# 根据月将,时辰定天盘
month_index = constant.in_use.index(lunar.cur_jq_name)
hour_index = lunar.hour_index
# 通过节气获得月将的地支下标 a
# 通过时间获得时辰,得到地支下标 b
# 定天盘位置,并和地盘位置对齐,天盘中a下标对应的地支应该和地盘中b下标对应的地支位置一致
tp = [None] * 12
for i in range(12):
    tp[(hour_index + i) % 12] = dp[(month_index + i) % 12]

day_gan = lunar.day_gan
day_zhi = lunar.day_zhi
# 获取四课
# 天干找到所寄的地支
first = constant.ke_mapping[day_gan]
# 地盘固定不变,通过在地盘的位置找到天盘对应的地支
second = tp[first['index']]
first = first['name']
third = dp[lunar.day_zhi_index]
forth = tp[constant.Zhi.index(third)]
