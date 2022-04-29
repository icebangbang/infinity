import pymongo
import logging

myclient = pymongo.MongoClient("mongodb://root:whosyourdaddy$879@39.105.104.215:20017/")
db = myclient['stock']

myclient_184 = pymongo.MongoClient("mongodb://root:whosyourdaddy$879@172.16.1.184:20017/")
db_184 = myclient_184['stock']

def init_db(app):
    global db
    global myclient
    myclient = pymongo.MongoClient(app.config['MONGO_URL'])
    db = myclient['stock']
    return db


