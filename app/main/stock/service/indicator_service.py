from app.main.db.mongo import db


def get_latest_update_time(name):
    """
    获取pmi最近更新时间
    :return:
    """
    indicator_sync_record = db['indicator_sync_record']
    entity = indicator_sync_record.find_one({"name":name})
    if entity is not None:
        return entity['update_time']
    return None




if __name__ == "__main__":
    r = get_latest_update_time("pmi")
    pass