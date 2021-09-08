from app.main.stock import stock_concept
from app.main.stock.api import stock_info
import logging as log
import pymongo

log.info("开始获取股票列表")
stock_list = stock_info.get_stock_list()
log.info("开始获取概念列表")
concepts = stock_concept.get_all_concept()
log.info("总共有{}个概念".format(len(concepts)))

myclient = pymongo.MongoClient("mongodb://admin:123456@101.37.24.40:20017/")
mydb = myclient["stock"]
stock_detail = mydb["stock_detail"]
concept_detail = mydb["concept_detail"]


for stock in stock_list:
    stock['concept'] = list()

stock_dict = {v['code']: v for v in stock_list}
concept_list = []
for index,concept in enumerate(concepts):
    label = concept['板块名称']
    code = concept['板块代码']
    concept_dict = {"concept":label,"code":code,"codes":list()}
    concept_list.append(concept_dict)

    log.info("正在获取:{} {}".format(label,str(index)))
    mappings = stock_concept.get_concept_mapping(label)
    for mapping in mappings:
        if mapping['代码'] == '暂无成份股数据':
            log.info("{} 暂无成分股数据".format(mapping['代码']))
            continue
        if mapping['代码'] in stock_dict.keys():
            concept_dict["codes"].append(mapping['代码'])
            stock_dict[mapping['代码']].get('concept').append(label)
        else:
            log.info("{}不在字典内".format(mapping['代码']))

    t = []
    for concept in concept_list:
        for k,v in concept.items():
            t.append({"concept":k,"codes":v})





# 清空
stock_detail.remove()
concept_detail.remove()

x = stock_detail.insert_many(stock_dict.values())
concept_detail.insert_many(concept_list)

print(x.inserted_ids)
