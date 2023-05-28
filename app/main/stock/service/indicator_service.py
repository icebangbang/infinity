from app.main.db.mongo import db


def get_latest_update_items()->dict:
    """
    获取pmi最近更新时间
    :return:
    """
    indicator_sync_record = db['indicator_sync_record']
    entities = list(indicator_sync_record.find({}))

    return { entitiy['name']:entitiy['update_time'] for entitiy in entities}




if __name__ == "__main__":
    r = get_latest_update_items()
    pass