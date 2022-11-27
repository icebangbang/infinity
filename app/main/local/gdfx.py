import akshare as ak

from app.main.stock.dao import stock_dao
from app.main.utils import stock_util

stock_detail_list = stock_dao.get_all_stock({"code":1,"name":1})

total = list()
for index,stock_detail in enumerate(stock_detail_list):
    if index <= 1110: continue
    code = stock_detail['code']
    name = stock_detail['name']
    code = stock_util.basic_belong(code)+code
    stock_gdfx_free_top_10_em_df = ak.stock_gdfx_free_top_10_em(symbol=code, date="20220930")
    if stock_gdfx_free_top_10_em_df is None: continue
    gd_list = list(stock_gdfx_free_top_10_em_df['股东名称'])
    print(index,code,name)
    total = list()
    for gd in gd_list:
        if "养老" in gd:
            print(code,name,gd)
            total.append("{},{},{}".format(code,name,gd))
print(total)
