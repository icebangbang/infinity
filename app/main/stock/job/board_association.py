"""
个股反向关联个股
"""
from app.main.stock.dao import stock_dao
from app.main.db.mongo import db
from datetime import datetime

def associate():
    stocks = stock_dao.get_all_stock()
    board_detail = db['board_detail']
    stock_detail = db['stock_detail']

    for index,stock in enumerate(stocks):
        code = stock['code']

        detail = board_detail.find_one({"type":2,"codes":{"$in":[code]}})

        if detail is None:
            print(stock['name'])
            continue
        board = detail['board']

        stock_detail.update_one({"code":code},{"$set":dict(industry=board,update_time = datetime.now())})
        print("{}，{} 属于 {}".format(index,stock['name'],detail['board']))

if __name__ == "__main__":
    associate()