"""
etf分词
"""
from app.main.stock.dao import etf_dao

etf_list = etf_dao.get_eft_list()
key_words = ['港', '恒生', '创业', '债', '上证', '中证', '沪深', '货','华']
in_need = "电池"
for etf in etf_list:
    name = etf['name']
    code = etf['code']

    is_ok = True
    for key_word in key_words:
        if key_word in name:
            is_ok = False

    # if is_ok:
    #      print(name,code)
    #      print(etf['money'])
