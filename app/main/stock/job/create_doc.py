from app.main.db.mongo import db


def create_doc(doc_name):
    collist = db.list_collection_names()
    if doc_name not in collist:
        data_set = db[doc_name]
        data_set.insert_one({})
        data_set.remove({})


def run():
    db.trade_point.create_index([("code", 1)])
    db.trade_point.create_index([("date", -1), ("code", 1)])
    docs = ["k_line_day", "board_k_line_day", "stock_feature", "stock_detail", "stock_value", "report_data"]
    for doc in docs:
        create_doc(doc)
    db.k_line_month.create_index([("date", 1), ("code", 1)])
    db.board_k_line_day.create_index([("name", 1), ("date", 1)])
    db.board_k_line_day.create_index([("name", 1)])
    db.k_line_day.create_index([("code", 1)])
    db.k_line_day.create_index([("date", 1), ("code", 1)])
    db.k_line_day.create_index([("date", 1)])
    db.special_stock.create_index([("date", 1)])

    db.stock_feature.create_index([("code", 1)])
    db.stock_feature.create_index([("date", 1), ("code", 1)])
    db.stock_detail.create_index([("code", 1)])
    db.stock_value.create_index([("date", 1), ("code", 1)])
    db.market_status.create_index([("date", 1)])

    db.rps_anslysis.create_index([("code", 1), ("date", 1)])


if __name__ == "__main__":
    run()
