from app.main.db.mongo import db


def select_by_date(board, start, end,trend):
    stock_training_picker = db['stock_training_picker']
    return list(stock_training_picker.find({"board": board,
                                     "trend": trend,
                                     "start_scope": {"$gte": start},
                                     "end_scope": {"$lte": end}}))
