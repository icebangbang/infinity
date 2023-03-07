"""
变量集,用于描述干支之间的关系
"""



Gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
Zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ShX = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]

numCn = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
Week = ["日", "一", "二", "三", "四", "五", "六"]
jqmc = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露",
        "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]
ymc = ["十一", "十二", "正", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
rmc = ["初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十", "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九",
       "二十", "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十", "卅一"]

five_elements = ["金", "水", "木", "火", "土"]

position = ["西", "北", "东", "南", "中"]

# 24节气中,六壬主要用到的节气
in_use = ['大寒', '冬至', '小雪', '霜降', '秋分', '处暑', '大暑', '夏至', '小满', '谷雨', '春分', '雨水']

jia = dict(name="甲", index=0, yy='阳', yy_index=1, fe="木", fe_index=2, po="东", po_index=2)
bing = dict(name="丙", index=2, yy="阳", yy_index=1, fe="火", fe_index=3, po="南", po_index=3)
wu4 = dict(name="戊", index=4, yy="阳", yy_index=1, fe="土", fe_index=4, po="中", po_index=4)
geng = dict(name="庚", index=6, yy="阳", yy_index=1, fe="金", fe_index=0, po="西", po_index=0)
ren = dict(name="壬", index=8, yy="阳", yy_index=1, fe="水", fe_index=1, po="北", po_index=1)
yi = dict(name="乙", index=1, yy='阴', yy_index=0, fe="木", fe_index=2, po="东", po_index=2)
ding = dict(name="丁", index=3, yy="阴", yy_index=0, fe="火", fe_index=3, po="南", po_index=3)
ji = dict(name="己", index=5, yy="阴", yy_index=0, fe="土", fe_index=4, po="中", po_index=4)
xin = dict(name="辛", index=7, yy="阴", yy_index=0, fe="金", fe_index=0, po="西", po_index=0)
kui = dict(name="癸", index=9, yy="阴", yy_index=0, fe="水", fe_index=1, po="北", po_index=1)

zi = dict(name="子", index=0, yy="阳", yy_index=1, fe="水", fe_index=1, po="北", po_index=1)
yin = dict(name="寅", index=2, yy='阳', yy_index=1, fe="木", fe_index=2, po="东", po_index=2)
chen = dict(name="辰", index=4, yy="阳", yy_index=1, fe="土", fe_index=4, po="中", po_index=4)
wu = dict(name="午", index=6, yy="阳", yy_index=1, fe="火", fe_index=3, po="南", po_index=3)
shen = dict(name="申", index=8, yy="阳", yy_index=1, fe="金", fe_index=0, po="西", po_index=0)
xu = dict(name="戌", index=10, yy="阳", yy_index=1, fe="土", fe_index=4, po="中", po_index=4)
chou = dict(name="丑", index=1, yy="阴", yy_index=0, fe="土", fe_index=4, po="中", po_index=4)
mao = dict(name="卯", index=3, yy='阴', yy_index=0, fe="木", fe_index=2, po="东", po_index=2)
si = dict(name="巳", index=5, yy="阴", yy_index=0, fe="火", fe_index=3, po="南", po_index=3)
wei = dict(name="未", index=7, yy="阴", yy_index=0, fe="土", fe_index=4, po="中", po_index=4)
you = dict(name="酉", index=9, yy="阴", yy_index=0, fe="金", fe_index=0, po="西", po_index=0)
hai = dict(name="亥", index=11, yy="阴", yy_index=0, fe="水", fe_index=1, po="北", po_index=1)

# 天干对应的阴阳属性,0代表阴,1代表阳
gan_yin_yang = {"甲": jia,
                "丙": bing,
                "戊": wu4,
                "庚": geng,
                "壬": ren,
                "乙": yi,
                "丁": ding,
                "己": ji,
                "辛": xin,
                "癸": kui}
# 地支对应的阴阳属性,0代表阴,1代表阳
zhi_yin_yang = {"子": zi,
                "寅": yin,
                "辰": chen,
                "午": wu,
                "申": shen,
                "戌": xu,
                "丑": chou,
                "卯": mao,
                "巳": si,
                "未": wei,
                "酉": you,
                "亥": hai}
# 天干地支的阴阳属性
yin_yang = gan_yin_yang.update(zhi_yin_yang)

# 五行
five_elements_gan_mapping = {"金": [geng, xin], "水": [ren, kui], "木": [jia, yi], "火": [bing, ding], "土": [wu, ji]}
five_elements_zhi_mapping = {"金": [shen, you], "水": [zi, hai], "木": [yin, mao], "火": [wu, si],
                             "土": [chen, chou, xu, wei]}

ke_mapping = {"甲": yin, 0: yin,  # 甲寄寅宮
              "乙": chen, 1: chen,  # 乙寄辰宮
              "丙": si, 2: si,  # 丙寄巳宮
              "丁": wei, 3: wei,  # 丁寄未宮
              "戊": si, 4: si,  # 戊寄巳宮
              "己": wei, 5: wei,  # 己寄未宮
              "庚": shen, 6: shen,  # 庚寄申宮
              "辛": xu, 7: xu,  # 辛寄戌宮
              "壬": hai, 8: hai,  # 壬寄亥宮
              "癸": chou, 9: chou,  # 癸寄丑宮
              }


def get_sheng(element, get_word=True):
    """
    获取选中五行相生的属性
    five_elements中,每个五行的下一个为生,跨一个为克
    :param element: 五行的值,文本或者index
    :param get_word: 是否返回文本
    :return:
    """
    if isinstance(element, int) is not True:
        element = five_elements.index(element)
    index = (element + 1) % 5
    if get_word is not True:
        return index
    else:
        return five_elements[index]


def get_ke(element, get_word=True):
    """
    获取选中五行相克的属性
    five_elements中,每个五行的下一个为生,跨一个为克
    :param element: 五行的值,文本或者index
    :param get_word: 是否返回文本
    :return:
    """
    if isinstance(element, int) is not True:
        element = five_elements.index(element)
    index = (element + 2) % 5
    if get_word is not True:
        return index
    else:
        return five_elements[index]
