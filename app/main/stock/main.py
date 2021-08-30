from app.main.stock import stock_info, stock_concept
import logging as log
import pymongo

log.info("开始获取股票列表")
stock_list = stock_info.get_stock_list()
log.info("开始获取概念列表")
concepts = stock_concept.get_all_concept()
log.info("总共有{}个概念".format(len(concepts)))

for stock in stock_list:
    stock['concept'] = list()

stock_dict = {v['code']: v for v in stock_list}

for index,concept in enumerate(concepts):
    label = concept['name']
    log.info("正在获取:{} {}".format(label,str(index)))
    mappings = stock_concept.get_concept_mapping(label)
    for mapping in mappings:
        if mapping['代码'] == '暂无成份股数据':
            log.info("{} 暂无成分股数据".format(mapping['代码']))
            continue
        if mapping['代码'] in stock_dict.keys():
            stock_dict[mapping['代码']].get('concept').append(label)
        else:
            log.info("{}不在字典内".format(mapping['代码']))

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["stock"]
stock_detail = mydb["stock_detail"]

# 清空
# stock_detail.remove()

x = stock_detail.insert_many(stock_dict.values())
print(x.inserted_ids)
