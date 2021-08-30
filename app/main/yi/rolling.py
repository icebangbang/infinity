import random
from datetime import datetime
from functools import reduce

import sys


def get_yinyang(r):
    if r == 0:  # 太阴
        return 6
    if r == 2:  # 少阴
        return 7
    if r == 1:  # 少阳
        return 8
    if r == 3:  # 太阳
        return 9


def get_binary(r):
    if r == 0:  # 太阴
        return '0'
    if r == 2:  # 少阴
        return '0'
    if r == 1:  # 少阳
        return '1'
    if r == 3:  # 太阳
        return '1'


def get_format(num):
    if num == 6:
        return '- - o'
    if num == 7:
        return '- -'
    if num == 8:
        return '---'
    if num == 9:
        return '--- o'


def get_fix_yao(left):
    a = int(left / 6)  # 循环次数
    b = left % 6
    start = 0 if a % 2 != 0 else 1

    if b == 0:
        fix_yao = 1 if start == 1 else 6
    else:
        fix_yao = b if start == 1 else 6 - b + 1
    return fix_yao


which_thing = input("求占何事：")

binarys = []
nums = []
base_shape = []
now = datetime.now()
simple_index = (now.hour * 100 + now.minute) % 6
simple_index = 6 if simple_index == 0 else simple_index

# 回车驱动摇卦,执行6次
for i in range(6):
    print("按回车开始第{}摇卦".format(i + 1))
    input()
    coin_1 = random.randint(0, 1)
    coin_2 = random.randint(0, 1)
    coin_3 = random.randint(0, 1)
    r = coin_1 + coin_2 + coin_3
    flag = get_yinyang(r)
    binarys.append(get_binary(r))
    nums.append(flag)
    formatted = get_format(flag)
    base_shape.append(formatted)
    print(formatted)

# 一个卦的总营数
full_flag = reduce(lambda x, y: x + y, nums)
# 营数的驱动数
left = 55 - full_flag
# 营数从下后上,再从下到上的,最后落到的爻上,称之为值守
fix_yao = get_fix_yao(left)

# 动爻是否处于值守,弱势
use_yao = False
print("求占:{}".format(which_thing))
print("应在{}爻".format(fix_yao))

if nums[fix_yao - 1] in [6, 9]:
    use_yao = True
    print("爻动,用爻辞来判断")
else:
    print("爻不动,用卦辞来判断")

print("当前时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

binary_str = ''.join(binarys)
print(binary_str)

base_shape[fix_yao - 1] = base_shape[fix_yao - 1] + " <- "
for n in list(reversed(base_shape)):
    print(n)
