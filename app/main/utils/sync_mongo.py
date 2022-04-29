from time import sleep

from pymongo import MongoClient, ASCENDING
from pymongo.cursor import CursorType
from pymongo.errors import AutoReconnect
from app.main.db.mongo import myclient,db_184
from datetime import datetime
import queue
from threading import Thread


# Time to wait for data or connection.
_SLEEP = 1.0

q = queue.Queue(-1)


def f(queue):
    while True:
        if not q.empty():
            doc = queue.get()
            b = db_184['k_line_day']
            if doc['op'] == "u":
                _id = doc['o']['_id']
                b.update_one({"_id":_id},{"$set": doc['o']},upsert=True)
            print(doc)


t = Thread(target=f, args=(q,))
t.start()

oplog = myclient.local.oplog.rs
stamp = oplog.find().sort('$natural', ASCENDING).limit(-1).next()['ts']

while True:
    kw = {}
    kw['filter'] = {'ts': {'$gt': stamp}}
    kw['cursor_type'] = CursorType.TAILABLE_AWAIT
    kw['oplog_replay'] = True

    cursor = oplog.find(**kw)

    try:
        while cursor.alive:
            for doc in cursor:
                stamp = doc['ts']
                ns = doc['ns']

                if ns in ['stock.k_line_day']:
                    q.put(doc)

    except AutoReconnect:
        print("reconnect")
