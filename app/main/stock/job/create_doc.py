from app.main.db.mongo import db


def create_doc():
    collist = db.list_collection_names()

    if "k_line_day" not in collist:
        data_set = db["k_line_day"]
        # data_set.insert({"code":1,"date":'2021-10-20'})
        # db.k_line_day.create_index({"date":1})
        data_set.remove({})

    if "board_k_line" not in collist:
        data_set = db["board_k_line"]
        data_set.remove({})

    db.k_line_day.create_index([("code", 1), ("date", 1)])
    db.k_line_day.create_index([("code", 1)])
    db.board_k_line.create_index([("name", 1), ("date", 1)])
    db.board_k_line.create_index([("name", 1)])

    stock_detail = db["stock_detail"]


if __name__ == "__main__":
    create_doc()
