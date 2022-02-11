import requests
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree
from datetime import datetime
from app.main.db.mongo import db
from app.main.utils import date_util


def sync_basic():
    r = requests.get("https://api.hzfc.cn/hzfcweb_ifs/interaction/scxx")
    text = str(r.content, 'utf8')
    temp_df = pd.read_html(text)
    items = temp_df[0].to_dict(orient="records")
    new_items = [dict(type=item['房屋用途'],
                      deal=item['成交套数'].replace("套", ""),
                      area=item['成交面积'].replace("m²", ""),
                      date=date_util.get_start_of_day(datetime.now()),
                      city="杭州",
                      update_time=datetime.now()) for item in items]
    collection = db['house_basic']
    for new_item in new_items:
        collection.update_one({"city": new_item['city'],
                               "date": new_item['date'],
                               "type": new_item['type']}, {"$set": new_item}, upsert=True)


def sync_detail():
    data_dict = {}
    r = requests.get("https://api.hzfc.cn/hzfcweb_ifs/interaction/scxx")
    text = str(r.content, 'utf8')
    # temp_df = pd.read_html(text)

    html = etree.HTML(text)
    # soup = BeautifulSoup(text, 'lxml')
    items = html.xpath('//*[@id="con1"]/div[@class="list-item hehe"]')
    for item in items:
        if len(item) == 0: continue
        name = item[0].text

        # if name == '合计': name = "商品房合计"

        data = data_dict.get(name, {})
        data['city'] = "杭州"
        data['name'] = name
        data['deal'] = int(item[1].text.replace("套", ""))
        data['area'] = float(item[2].text.replace("m²", ""))
        data['house_deal'] = int(item[3].text.replace("套", ""))
        data['house_area'] = float(item[4].text.replace("m²", ""))
        data['date'] = date_util.get_start_of_day(datetime.now())
        data['update_time'] = datetime.now()

        data_dict[name] = data

    # print()
    items = html.xpath('//*[@id="con3"]/div[@class="list-item hehe"]')
    for item in items:
        if len(item) == 0: continue
        name = item[0].text

        # if name == '合计':
        #     name = "二手房合计"

        data = data_dict.get(name, {})
        data['secondhand_deal'] = int(item[1].text.replace("套", ""))
        data['secondhand_area'] = float(item[2].text.replace("m²", ""))
        data['secondhand_house_deal'] = int(item[3].text.replace("套", ""))
        data['secondhand_house_area'] = float(item[4].text.replace("m²", ""))

        data_dict[name] = data

    collection = db['house_detail']

    for data in data_dict.values():
        collection.update_one({"city": data['city'],
                               "name": data['name'],
                               "date": data['date']},
                              {"$set": data}, upsert=True)


def sync_on_sale():
    data_dict = {}
    r = requests.get("https://api.hzfc.cn/hzfcweb_ifs/interaction/scxx")
    text = str(r.content, 'utf8')
    # temp_df = pd.read_html(text)

    html = etree.HTML(text)
    items = html.xpath('//*[@id="scroll-wrap"]/div[@class="list-item"]')
    for item in items:
        name = item[0].text
        data = data_dict.get(name, {})
        # if name == '合计': continue
        data['city'] = "杭州"
        data['name'] = name
        data['on_sale'] = int(item[1].text.replace("套", ""))
        data['on_sale_area'] = float(item[2].text.replace("m²", ""))
        data['on_sale_house'] = int(item[3].text.replace("套", ""))
        data['on_sale_house_area'] = float(item[4].text.replace("m²", ""))
        data['date'] = date_util.get_start_of_day(datetime.now())
        data['update_time'] = datetime.now()

        data_dict[name] = data

    collection = db['house_on_sale']
    for data in data_dict.values():
        collection.update_one({"city": data['city'],
                               "name": data['name'],
                               "date": data['date']},
                              {"$set": data}, upsert=True)


# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options # => 引入Chrome的配置
# ch_options = Options()
# # ch_options.add_argument("--headless")  # => 为Chrome配置无头模式
#
#
# driver = webdriver.Chrome("/Users/lifeng/Work/Python/dao/other/chromedriver",options=ch_options) # => 注意这里的参数
# driver.get("http://fgj.hangzhou.gov.cn/col/col1229440802/index.html")
# driver.implicitly_wait(2000)
# html = driver.page_source

if __name__ == "__main__":
    sync_on_sale()
    sync_detail()
    sync_basic()
