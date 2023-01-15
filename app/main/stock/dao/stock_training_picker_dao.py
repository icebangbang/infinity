from app.main.db.mongo import db


def select_by_date(board, start, end,year,trend):
    stock_training_picker = db['stock_training_picker']
    return list(stock_training_picker.find({"board": board,
                                     "trend": trend,
                                     "year":{"$in":[year]},
                                     "start_scope": {"$gte": start},
                                         "end_scope": {"$lte": end}}))

def update(result):
    db['stock_training_picker'].update_one({"start_scope": result['start_scope'],
                                            "code": result['code'],
                                            "board": result['board'],
                                            "trend": "up"},
                                           {"$set": result}, upsert=True)
