from app.main.db.mongo import db
collist = db.list_collection_names()

if "k_line_day" not in collist:
    data_set = db["k_line_day"]
    # data_set.insert({"code":1,"date":'2021-10-20'})

    db.k_line_day.create_index([("code", 1), ("date", 1)])
    # db.k_line_day.create_index({"date":1})
    data_set.remove({})

stock_detail = db["stock_detail"]
