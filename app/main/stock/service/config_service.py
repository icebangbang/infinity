from app.main.db.mongo import db


def save_query_param(data):
    query_store = db["ind_query_store"]
    query_store.insert(data)