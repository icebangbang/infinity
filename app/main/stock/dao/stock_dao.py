from app.main.db.mongo import db

def get_all_stock():
    my_set = db['stock_detail']
    data = list(my_set.find({},dict(code=1,date=1,belong=1,name=1,_id=0)))
    return data


