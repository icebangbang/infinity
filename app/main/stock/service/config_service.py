from app.main.db.mongo import db


def save_query_param(data):
    query_store = db["ind_query_store"]
    query_store.insert(data)

def get_query_param(key):
    query_store = db["ind_query_store"]
    result = query_store.find_one({"key":key})
    return result['params']