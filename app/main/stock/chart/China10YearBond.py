from app.main.stock.chart.Line import Line
from app.main.db.mongo import db
from app.main.stock.dao import stock_dao
from app.main.utils import date_util
from datetime import datetime
import pandas as pd
import requests
import chardet

class China10YearBond(Line):
    """
    市场涨跌情况分析图表
    """

    def generate(self,**kwargs):
        header = {
            "Accept": "text/plain, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection": "keep-alive",
            "Content-Length": "277",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": 'PHPSESSID=bqbo78k07hdjpbhd8aboctjube; SideBlockUser=a:2:{s:10:"stack_size";a:1:{s:11:"last_quotes";i:8;}s:6:"stacks";a:1:{s:11:"last_quotes";a:1:{i:0;a:3:{s:7:"pair_ID";s:5:"29227";s:10:"pair_title";s:0:"";s:9:"pair_link";s:37:"/rates-bonds/china-10-year-bond-yield";}}}}; geoC=JP; ab_billboard_test=billboard_default; adBlockerNewUserDomains=1657113168; udid=acbaacbdc2759410986c4602334c103e; smd=acbaacbdc2759410986c4602334c103e-1657113168; __cflb=0H28uxmf5JNxjDUC6W38wZXb1CUFbuyf1TCUYnbsdtQ; __gpi=UID=0000076bf445ff4e:T=1657113171:RT=1657113171:S=ALNI_MZZsrS51-Nn3XKvylSH1cpbrVdP4w; _gaexp=GAX1.2.HHsGkqhgQ5WRQQdiTFpBgw.19224.x314; protectedMedia=2; pms={"f":2,"s":2}; _fbp=fb.1.1657113173563.9647677; _ga=GA1.2.1098670358.1657113172; _gid=GA1.2.1228527652.1657113174; Hm_lvt_a1e3d50107c2a0e021d734fe76f85914=1657113174; G_ENABLED_IDPS=google; adsFreeSalePopUp=3; g_state={"i_l":0}; __gads=ID=5b072329d50e2c71-227c459e0bd500f3:T=1657113171:S=ALNI_MZAkKW5DRZHQqblZc02xbAYb6ITRg; comment_notification_239938116=1; Adsfree_conversion_score=0; adsFreeSalePopUp9326b41e64bae57737f3bc6ad67a2e0b=1; r_p_s_n=1; UserReactions=true; nyxDorf=MjZkNzNmN3VjPWhsZClhZzJlZSBjbDA3; invpc=10; Hm_lpvt_a1e3d50107c2a0e021d734fe76f85914=1657115639; _gat_allSitesTracker=1; ses_id=MX9mJzY5NT1iJjo8MGE3NjZuNmRmYmdtZWU0NjQ1YnRgdDY4ZTI0cmZpaCZnZGJ+Y2IxMWM2YGFnMmY7M2BuODE0Zjc2YzVqYmA6NDBkNzU2bjZtZjNnZ2VsNGI0Z2JvYDM2NWUyNDFmYmg9Z21ibmNxMS1jJ2BxZzVmNjNybikxPmYnNmY1a2JnOjMwajczNmI2OWZiZzdlZTRiNGBiemAr; __cf_bm=e2U1mfkLJIoPUxDhgzVYwdKAgIkFpFZRVzXUJfry2e0-1657116255-0-AcJJ/QitfF7j4O3szOprcajdjzTpTiVJI06ulq/wozThId8mbcx4ns6eh/f1iFweN7oc3x3xlaI4z1vqP3Zi5UM=',
            "Host": "cn.investing.com",
            "Origin": "https://cn.investing.com",
            "Referer": "https://cn.investing.com/rates-bonds/china-10-year-bond-yield-historical-data",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0",
            "X-Requested-With": "XMLHttpRequest"
        }
        d = requests.post("https://cn.investing.com/instruments/HistoricalDataAjax",
                          data={
                              "curr_id": 29227,
                              "smlID": 204958,
                              "header": "中国十年期国债收益率历史数据",
                              "st_date": "2022/04/01",
                              "end_date": "2022/07/06",
                              "interval_sec": "Daily",
                              "sort_col": "date",
                              "sort_ord": "DESC",
                              "action": "historical_data"
                          },headers=header)
        text = d.text
        temp_df = pd.read_html(text)[0]

        return None

if __name__ == "__main__":
    bond = China10YearBond()
    bond.generate()